# Week 1 Post-Lab Questions

### 1. Definitions
- **Node:** A node is a process that performs computation and communicates with other nodes in the ROS graph.
- **Topic:** A topic is a named bus over which nodes exchange messages using a publish-subscribe model.
- **Package:** A package is the organizational unit for ROS 2 code, containing everything needed (code, data, dependencies) to run a specific function.
- **Workspace:** A workspace is a directory structure (like `ros2_ws`) where ROS 2 packages are developed, built, and installed.

### 2. Why is sourcing required?
Sourcing (e.g., `source install/setup.bash`) is required to update the terminal's environment variables so it knows where to find ROS 2 commands and your specific packages. If you do not source, the terminal will return "command not found" errors for ROS-specific tools.

### 3. Purpose of `colcon build`
The purpose of `colcon build` is to compile the source code and organize it into a format that ROS 2 can execute. It generates the following folders:
- `build`: Where intermediate files are stored.
- `install`: Where the final executable and setup scripts are placed.
- `log`: Where build logs are stored for debugging.

### 4. Entry Points in `setup.py`
The `console_scripts` entry point acts as a map that tells ROS 2: "When I type the command `simple_node`, look inside the `my_first_pkg` folder, find the `simple_node.py` file, and run the `main` function."

### 5. Publisher/Subscriber Diagram


```text
+----------------+   Publishes   +----------------+   Subscribes   +----------------+
| Publisher Node | ------------> |     Topic      | -------------> | Subscriber Node|
|   (Talker)     |   (Message)   |   (/chatter)   |   (Message)    |   (Listener)   |
+----------------+               +----------------+                +----------------+