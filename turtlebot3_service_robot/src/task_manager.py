#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import rospy
import yaml
import math
from enum import Enum

import actionlib
from std_msgs.msg import String
from std_srvs.srv import Trigger
from move_base_msgs.msg import MoveBaseAction, MoveBaseGoal
from geometry_msgs.msg import Quaternion
from actionlib_msgs.msg import GoalStatus


class State(Enum):
    INIT           = "INIT"
    GO_TO_LOCATION = "GO_TO_LOCATION"
    QR_VERIFY      = "QR_VERIFY"
    REPORT         = "REPORT"
    NEXT_LOCATION  = "NEXT_LOCATION"
    FINISH         = "FINISH"


class TaskResult(Enum):
    SUCCESS = "SUCCESS"
    FAIL    = "FAIL"
    SKIPPED = "SKIPPED"


def yaw_to_quaternion(yaw):
    q = Quaternion()
    q.x = 0.0
    q.y = 0.0
    q.z = math.sin(yaw / 2.0)
    q.w = math.cos(yaw / 2.0)
    return q


class TaskManager:
    def __init__(self):
        rospy.init_node('task_manager', anonymous=False)

        mission_file = rospy.get_param('~mission_file', '')
        if not mission_file:
            import rospkg
            rp = rospkg.RosPack()
            pkg_path = rp.get_path('turtlebot3_service_robot')
            mission_file = pkg_path + '/config/mission.yaml'

        self.nav_retries    = int(rospy.get_param('~nav_retries', 1))
        self.qr_retries_def = int(rospy.get_param('~qr_retries', 2))
        self.timeout_def    = float(rospy.get_param('~timeout', 90.0))

        rospy.loginfo("[TaskManager] Mission: %s", mission_file)
        with open(mission_file, 'r', encoding='utf-8') as f:
            self.mission = yaml.safe_load(f)

        self.status_pub = rospy.Publisher('/task_manager/status', String, queue_size=10, latch=True)
        self.report_pub = rospy.Publisher('/task_manager/report', String, queue_size=10, latch=True)

        rospy.loginfo("[TaskManager] move_base bekleniyor...")
        self.move_base = actionlib.SimpleActionClient('move_base', MoveBaseAction)
        self.move_base.wait_for_server(rospy.Duration(30))
        rospy.loginfo("[TaskManager] move_base hazır.")

        rospy.loginfo("[TaskManager] QR reader bekleniyor...")
        rospy.wait_for_service('/qr_reader/trigger', timeout=30)
        self.qr_trigger = rospy.ServiceProxy('/qr_reader/trigger', Trigger)
        rospy.loginfo("[TaskManager] QR reader hazır.")

        self.results = {}

    def _set_state(self, state, extra=""):
        msg = state.value + (f" — {extra}" if extra else "")
        self.status_pub.publish(String(data=msg))
        rospy.loginfo("[%s] %s", state.value, extra)

    def run(self):
        rospy.loginfo("=" * 50)
        rospy.loginfo("  KTÜN Servis Robotu Başlatıldı")
        rospy.loginfo("=" * 50)

        self._set_state(State.INIT, "Sistem hazır")
        rospy.sleep(1.0)

        locations = self.mission['locations']

        for i, loc_name in enumerate(locations):
            loc_cfg     = self.mission[loc_name]
            timeout     = float(loc_cfg.get('timeout',    self.timeout_def))
            qr_retries  = int(  loc_cfg.get('qr_retries', self.qr_retries_def))
            qr_expected = loc_cfg['qr_expected']

            rospy.loginfo("-" * 40)
            rospy.loginfo("[%d/%d] Hedef: %s", i+1, len(locations), loc_name)

            # Beklenen QR'ı parametre olarak set et (simülasyon için)
            rospy.set_param('/qr_reader/expected_qr', qr_expected)

            # Navigasyon
            nav_ok = self._navigate(loc_name, loc_cfg, timeout)
            if not nav_ok:
                self._set_state(State.REPORT, f"{loc_name} → FAIL")
                self.results[loc_name] = TaskResult.FAIL
                continue

            # QR Doğrulama
            self._set_state(State.QR_VERIFY, f"{loc_name}")
            qr_result = self._verify_qr(loc_name, qr_expected, qr_retries)

            self._set_state(State.REPORT, f"{loc_name} → {qr_result.value}")
            self.results[loc_name] = qr_result

            self._set_state(State.NEXT_LOCATION, "")
            rospy.sleep(0.5)

        self._set_state(State.FINISH, "Tüm görevler tamamlandı")
        self._publish_report(locations)

    def _navigate(self, loc_name, loc_cfg, timeout):
        g = loc_cfg['goal']
        x, y, yaw = float(g['x']), float(g['y']), float(g['yaw'])

        for attempt in range(1, self.nav_retries + 2):
            self._set_state(State.GO_TO_LOCATION,
                            f"{loc_name} deneme {attempt} (x={x:.2f}, y={y:.2f})")

            goal = MoveBaseGoal()
            goal.target_pose.header.frame_id = "map"
            goal.target_pose.header.stamp    = rospy.Time.now()
            goal.target_pose.pose.position.x = x
            goal.target_pose.pose.position.y = y
            goal.target_pose.pose.orientation = yaw_to_quaternion(yaw)

            self.move_base.send_goal(goal)
            finished = self.move_base.wait_for_result(rospy.Duration(timeout))

            if finished and self.move_base.get_state() == GoalStatus.SUCCEEDED:
                rospy.loginfo("[TaskManager] %s — navigasyon BAŞARILI", loc_name)
                return True
            else:
                self.move_base.cancel_goal()
                rospy.logwarn("[TaskManager] %s — navigasyon başarısız, deneme %d", loc_name, attempt)
                rospy.sleep(3.0)

        return False

    def _verify_qr(self, loc_name, expected, retries):
        for attempt in range(1, retries + 2):
            rospy.loginfo("[QR] Deneme %d — beklenen: %s", attempt, expected)
            rospy.sleep(1.0)
            try:
                resp = self.qr_trigger()
            except rospy.ServiceException as e:
                rospy.logerr("[QR] Servis hatası: %s", e)
                rospy.sleep(2.0)
                continue

            if resp.success and resp.message.strip() == expected.strip():
                rospy.loginfo("[QR] ✓ Doğrulandı: %s", loc_name)
                return TaskResult.SUCCESS
            else:
                rospy.logwarn("[QR] Eşleşmedi: %s", resp.message)
                rospy.sleep(2.0)

        rospy.logwarn("[QR] %s → SKIPPED", loc_name)
        return TaskResult.SKIPPED

    def _publish_report(self, locations):
        sep = "=" * 45
        lines = [sep, "  GÖREV RAPORU", sep]
        s, f, sk = 0, 0, 0
        for loc in locations:
            r = self.results.get(loc, TaskResult.FAIL)
            icon = {"SUCCESS": "✓", "FAIL": "✗", "SKIPPED": "~"}[r.value]
            lines.append(f"  {icon} {loc:<28} {r.value}")
            if r == TaskResult.SUCCESS: s += 1
            elif r == TaskResult.FAIL:  f += 1
            else:                       sk += 1
        lines += [sep, f"  Başarılı:{s}  Atlanan:{sk}  Başarısız:{f}", sep]
        report = "\n".join(lines)
        rospy.loginfo("\n%s", report)
        self.report_pub.publish(String(data=report))


if __name__ == '__main__':
    try:
        TaskManager().run()
    except rospy.ROSInterruptException:
        pass
