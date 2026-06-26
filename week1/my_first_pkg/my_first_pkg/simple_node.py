import rclpy
from rclpy.node import Node
import os

class SimpleNode(Node):
    def __init__(self):
        super().__init__('simple_node')
        
        # Task 3: Declare parameter with default value
        self.declare_parameter('student_name', 'not_set')
        name_param = self.get_parameter('student_name').get_parameter_value().string_value
        
        # Task 2: Counter file path (Normal way: current directory)
        self.file_path = 'counter.txt'
        
        if os.path.exists(self.file_path):
            with open(self.file_path, 'r') as f:
                count = int(f.read())
        else:
            count = 0
            
        count += 1
        
        # Task 1 & 2: Output messages
        self.get_logger().info('Welcome to Mobile Robotics Lab')
        self.get_logger().info(f'Run count: {count}')
        
        # Task 3: Output name based on parameter status
        if name_param == 'not_set':
            self.get_logger().info('student_name not set')
        else:
            self.get_logger().info(f'Student Name: {name_param}')
        
        # Save updated count
        with open(self.file_path, 'w') as f:
            f.write(str(count))

def main(args=None):
    rclpy.init(args=args)
    node = SimpleNode()
    
    # Process the node briefly to ensure logs are printed, then exit
    rclpy.spin_once(node, timeout_sec=0.1)
    
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()