import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
import time

class VelocityPublisher(Node):
    def __init__(self):
        super().__init__('velocity_publisher')
        self.publisher_ = self.create_publisher(Twist, 'turtle1/cmd_vel', 10)
        # Start drawing 1 second after the node starts
        self.timer = self.create_timer(1.0, self.draw_triangle)

    def draw_triangle(self):
        self.timer.cancel() # Stop the timer so we only enter this loop once!
        msg = Twist()
        
        while rclpy.ok(): 
            
            for i in range(3): # Loop 3 times for a single triangle
                # 1. Move forward
                msg.linear.x = 2.0
                msg.angular.z = 0.0
                self.publisher_.publish(msg)
                time.sleep(2) # Drive forward for 2 seconds
                
                # 2. Turn 120 degrees (2.09 radians)
                msg.linear.x = 0.0
                msg.angular.z = 2.09 
                self.publisher_.publish(msg)
                time.sleep(1) # Turn for 1 second

def main(args=None):
    rclpy.init(args=args)
    velocity_publisher = VelocityPublisher()
    rclpy.spin(velocity_publisher)
    velocity_publisher.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()