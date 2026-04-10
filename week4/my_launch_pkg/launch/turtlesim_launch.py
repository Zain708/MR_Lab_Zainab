from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import ExecuteProcess

def generate_launch_description():
    return LaunchDescription([
        # Start the turtlesim simulator
        Node(package='turtlesim', executable='turtlesim_node', name='sim'),
        
        # Start the keyboard controller in a new window
        Node(package='turtlesim', executable='turtle_teleop_key', name='teleop', prefix='xterm -e'),
        
        # TASK 1: Automatically spawn turtle2 at coordinate (2.0, 2.0)
        ExecuteProcess(
            cmd=[['ros2 service call /spawn turtlesim/srv/Spawn "{x: 2.0, y: 2.0, theta: 0.0, name: \'turtle2\'}"']],
            shell=True
        )
    ])
