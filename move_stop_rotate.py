#!/usr/bin/env python3
import rospy
from sensor_msgs.msg import LaserScan
from geometry_msgs.msg import Twist

class MoveStopRotate:
    def __init__(self):
        rospy.init_node('move_stop_rotate')
        self.cmd_pub = rospy.Publisher('/cmd_vel', Twist, queue_size=10)
        self.scan_sub = rospy.Subscriber('/scan', LaserScan, self.scan_callback)
        self.twist = Twist()
        self.obstacle_distance = 0.5
        self.front_clear = True
        self.rate = rospy.Rate(10)

    def scan_callback(self, msg):
        # Önündeki mesafeye bak (0 derece)
        front_ranges = msg.ranges[0:10] + msg.ranges[350:360]
        front_ranges = [r for r in front_ranges if r > 0.01]
        
        if front_ranges:
            min_distance = min(front_ranges)
            if min_distance < self.obstacle_distance:
                self.front_clear = False
            else:
                self.front_clear = True

    def run(self):
        while not rospy.is_shutdown():
            if self.front_clear:
                # İleri git
                self.twist.linear.x = 0.2
                self.twist.angular.z = 0.0
                rospy.loginfo("İleri gidiliyor...")
            else:
                # Dur ve dön
                self.twist.linear.x = 0.0
                self.twist.angular.z = 0.5
                rospy.loginfo("Engel var! Dönülüyor...")
            
            self.cmd_pub.publish(self.twist)
            self.rate.sleep()

if __name__ == '__main__':
    try:
        robot = MoveStopRotate()
        robot.run()
    except rospy.ROSInterruptException:
        pass
