import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
import time

class InfiniteShapesController(Node):
    def __init__(self):
        super().__init__('infinite_shapes_controller')
        
        self.pub1 = self.create_publisher(Twist, 'turtle1/cmd_vel', 10)
        self.pub2 = self.create_publisher(Twist, 'turtle2/cmd_vel', 10)
        self.pub3 = self.create_publisher(Twist, 'turtle3/cmd_vel', 10)
        
        # Start the routine 1 second after launch
        self.timer = self.create_timer(1.0, self.draw_shapes)

    def draw_shapes(self):
        msg_circle = Twist()
        msg_square = Twist()
        msg_triangle = Twist()
        
        while rclpy.ok():
            
            # --- PHASE 1: MOVE FORWARD ---
            msg_circle.linear.x = 2.0
            msg_circle.angular.z = 1.2
            self.pub1.publish(msg_circle)
            
            msg_square.linear.x = 2.0
            msg_square.angular.z = 0.0
            self.pub2.publish(msg_square)
            
            msg_triangle.linear.x = 2.0
            msg_triangle.angular.z = 0.0
            self.pub3.publish(msg_triangle)
            
            time.sleep(1.5) 
            
            # --- PHASE 2: TURN ---
            self.pub1.publish(msg_circle) 
            
            msg_square.linear.x = 0.0
            msg_square.angular.z = 1.57 
            self.pub2.publish(msg_square)
            
            msg_triangle.linear.x = 0.0
            msg_triangle.angular.z = 2.09 
            self.pub3.publish(msg_triangle)
            
            time.sleep(1.0) 

def main(args=None):
    rclpy.init(args=args)
    node = InfiniteShapesController()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main() 