# URDF & 3D Robot Modeling (Lab 8)

Lab 8 — Mobile Robotics  
ROS 2 Humble | URDF | RViz Visualization

---

## What this is

This package (`my_robot_description`) was built for Lab 8 of the Mobile Robotics course. The objective was to design and build a custom differential drive mobile robot from scratch using the Unified Robot Description Format (URDF) and verify its joint coordinate transforms dynamically.

The robot features a multi-geometry physical build:
* **Chassis:** A blue rectangular box base link.
* **Actuation:** Two black cylindrical wheels driven via continuous joints.
* **Stability:** A white spherical caster wheel attached via a fixed joint.
* **Perception:** A red cylindrical LiDAR link mounted on top via a fixed joint.

---

## Package structure

```text
my_robot_description/
├── include/
├── launch/                  # (Empty for future custom launch scripts)
├── rviz/                    # (Empty for future custom RViz configurations)
├── src/                     # (Empty - pure description package, no C++ source)
├── urdf/
│   └── my_robot.urdf        # Main custom robot description file
├── CMakeLists.txt
└── package.xml
