#!/usr/bin/env python3
import rospy
import actionlib
from move_base_msgs.msg import MoveBaseAction, MoveBaseGoal

def go_to_goal(x, y):
    client = actionlib.SimpleActionClient('move_base', MoveBaseAction)
    client.wait_for_server()
    
    goal = MoveBaseGoal()
    goal.target_pose.header.frame_id = "map"
    goal.target_pose.header.stamp = rospy.Time.now()
    goal.target_pose.pose.position.x = x
    goal.target_pose.pose.position.y = y
    goal.target_pose.pose.orientation.w = 1.0
    
    client.send_goal(goal)
    client.wait_for_result()
    return client.get_state()

if __name__ == '__main__':
    rospy.init_node('go_to_points')
    
    points = [
        (0.0, 0.0),
        (1.0, 0.5),
        (-1.0, 0.5),
        (1.0, -0.5),
        (-1.0, -0.5)
    ]
    
    for i, (x, y) in enumerate(points):
        rospy.loginfo(f"Nokta {i+1} e gidiliyor: ({x}, {y})")
        result = go_to_goal(x, y)
        rospy.loginfo(f"Nokta {i+1} sonucu: {result}")
    
    rospy.loginfo("Tüm noktalara gidildi!")

