# Lab 2 Report: ROS 2 Topics, Services, and RQT

**Name:** Zainab  
**Course:** MCT-454L Mobile Robotics  

## 1. Objective
The objective of this lab was to become familiar with ROS 2 command-line tools and the `rqt` graphical interface by controlling a simulated robot (Turtlesim) using topics and services. 

## 2. Steps Followed and Observations

### Step 1: Launching the Simulation and Resetting
* **Action:** I launched the Turtlesim node from the terminal. Then, I opened the `rqt` GUI, navigated to the **Service Caller** plugin, and called the `/reset` service.
* **Observation:** As shown in the attached reset screenshot, calling the `/reset` service instantly cleared the simulation background and teleported the turtle back to its default starting position in the center of the screen.

### Step 2: Spawning a Second Turtle
* **Action:** Using the `rqt` Service Caller, I selected the `/spawn` service. I provided the specific coordinates `x=2.0`, `y=2.0`, `theta=0.0`, and assigned the name `'turtle2'`. 
* **Observation:** As shown in the attached spawn screenshot, upon calling the service, a second turtle successfully appeared in the bottom-left quadrant of the blue simulation window at the exact coordinates I requested.

### Step 3: Controlling the Turtles Independently
* **Action:** I opened the **Message Publisher** plugin in `rqt`. I selected the `/turtle2/cmd_vel` topic and set a continuous linear `x` velocity of 2.0 and an angular `z` velocity of 1.8. As an extra experiment, I also published velocity commands to the first turtle (`/turtle1/cmd_vel`) at the same time.
* **Observation:** The second turtle began driving in a continuous circle independently of the first turtle. By publishing to both topics simultaneously, I observed both turtles moving in circles at the same time, demonstrating that multiple nodes and topics can run concurrently in the ROS 2 ecosystem. (See attached screenshots for the independent and simultaneous control).

## 3. Conclusion
Through this exercise, I successfully demonstrated how to interact with a running ROS 2 node using `rqt`. I learned that services are used for quick, one-time requests (like resetting or spawning), while topics are used for continuous data streams (like sending velocity commands to drive the robot). 