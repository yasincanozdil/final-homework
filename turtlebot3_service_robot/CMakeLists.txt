cmake_minimum_required(VERSION 3.0.2)
project(turtlebot3_service_robot)

find_package(catkin REQUIRED COMPONENTS
  rospy
  std_msgs
  geometry_msgs
  nav_msgs
  sensor_msgs
  actionlib
  actionlib_msgs
  move_base_msgs
  tf
)

catkin_package(
  CATKIN_DEPENDS
    rospy
    std_msgs
    geometry_msgs
    nav_msgs
    sensor_msgs
    actionlib
    actionlib_msgs
    move_base_msgs
    tf
)

include_directories(
  ${catkin_INCLUDE_DIRS}
)

catkin_install_python(PROGRAMS
  src/task_manager.py
  src/qr_reader.py
  DESTINATION ${CATKIN_PACKAGE_BIN_DESTINATION}
)

install(DIRECTORY launch config maps worlds models
  DESTINATION ${CATKIN_PACKAGE_SHARE_DESTINATION}
)
