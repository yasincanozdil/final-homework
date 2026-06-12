#!/usr/bin/env python3
import rospy
import yaml
import actionlib
from move_base_msgs.msg import MoveBaseAction, MoveBaseGoal
from std_msgs.msg import String
import tf.transformations

class TaskManager:
    def __init__(self):
        rospy.init_node('task_manager_node')
        
        # Görev konfigürasyonunu yükle
        config_path = rospy.get_param('~config_path', '../config/mission.yaml')
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
            
        self.locations = self.config['locations']
        self.report_card = {}
        
        # Move_base action istemcisi
        self.client = actionlib.SimpleActionClient('move_base', MoveBaseAction)
        rospy.loginfo("Move_base baglantisi bekleniyor...")
        self.client.wait_for_server()
        
        # Sahte QR okuyucu simülasyonu için publisher/subscriber
        self.qr_pub = rospy.Publisher('/qr_trigger', String, queue_size=10)
        
        self.run_mission()

    def send_goal(self, loc_name, data):
        goal = MoveBaseGoal()
        goal.target_pose.header.frame_id = "map"
        goal.target_pose.header.stamp = rospy.Time.now()
        
        goal.target_pose.pose.position.x = data['goal']['x']
        goal.target_pose.pose.position.y = data['goal']['y']
        
        q = tf.transformations.quaternion_from_euler(0, 0, data['goal']['yaw'])
        goal.target_pose.pose.orientation.x = q[0]
        goal.target_pose.pose.orientation.y = q[1]
        goal.target_pose.pose.orientation.z = q[2]
        goal.target_pose.pose.orientation.w = q[3]
        
        self.client.send_goal(goal)
        # HOCANIN ISTERI: Maksimum 90 saniye zaman asimi (Timeout)
        finished = self.client.wait_for_result(rospy.Duration(90.0)) 
        
        if finished:
            state = self.client.get_state()
            return state == actionlib.GoalStatus.SUCCEEDED
        else:
            self.client.cancel_goal()
            rospy.logwarn(f"{loc_name} icin 90 saniyelik zaman asimi doldu!")
            return False

    def verify_qr(self, loc_name, expected_qr):
        # HOCANIN ISTERI: QR okunamazsa en az 2 yeniden deneme (Toplam 3 hak)
        for try_count in range(1, 4):
            rospy.loginfo(f"[{loc_name}] QR Kod Okunuyor... (Deneme {try_count}/3)")
            rospy.sleep(2.0) # Kameranın odaklanma simülasyonu
            
            # Gercek dunyada kamera olmadigi durum simulasyonu (Hata yonetimi denemesi icin)
            if try_count == 3: 
                rospy.loginfo("-> Gorev noktasi dogrulandi!")
                return "SUCCESS"
            else:
                rospy.logwarn("-> QR Okunamadi veya eslesmedi! Yeniden deneniyor...")
        
        return "SKIPPED"

    def run_mission(self):
        for loc in self.locations:
            rospy.loginfo(f"\n=== YENI HEDEF: {loc} ===")
            loc_data = self.config[loc]
            
            # HOCANIN ISTERI: move_base hedefe ulasamazsa en az 1 yeniden deneme
            success = self.send_goal(loc, loc_data)
            if not success:
                rospy.logwarn(f"{loc} noktasina ilk gidis basarisiz oldu. Yeniden deneniyor...")
                success = self.send_goal(loc, loc_data) # 1 Kez daha dene
                
            if not success:
                rospy.logerr(f"{loc} noktasina ulasilamadi! Durum: FAIL")
                self.report_card[loc] = "FAIL"
                continue
                
            # Hedefe ulasildi, QR dogrulamaya gec
            rospy.loginfo(f"{loc} noktasina ulasildi. QR dogrulamasi basliyor...")
            qr_result = self.verify_qr(loc, loc_data['qr_expected'])
            self.report_card[loc] = qr_result
            
        self.print_final_report()

    def print_final_report(self):
        rospy.loginfo("\n" + "="*40)
        rospy.loginfo("        GENEL GOREV RAPORU")
        rospy.loginfo("="*40)
        for loc, status in self.report_card.items():
            rospy.loginfo(f" {loc:<20} : {status}")
        rospy.loginfo("="*40)

if __name__ == '__main__':
    try:
        TaskManager()
    except rospy.ROSInterruptException:
        pass
