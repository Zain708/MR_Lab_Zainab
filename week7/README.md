# Autonomous Navigation (Lab 7)

Lab 7 — Mobile Robotics  
ROS 2 Humble | TurtleBot3 Burger | Gazebo + Nav2

---

## What this is

This package (`lab7_nav_pkg`) was built for Lab 7 of the Mobile Robotics course. The goal is to get a TurtleBot3 navigating autonomously through a set of waypoints using the ROS 2 Nav2 stack, with AMCL handling localization on a pre-built map.

The main node is `waypoint_navigator.py`. It sends goals to Nav2 sequentially using the `MapsToPose` action server. It waits for the robot to reach each point, dwells for a specified time (2 seconds), and then proceeds to the next goal.

---

## Setup & Build

Make sure you have the TurtleBot3 and Nav2 packages installed. 

First, navigate to your workspace and build the package:
```bash
cd ~/ros2_workspace
colcon build --packages-select lab7_nav_pkg
