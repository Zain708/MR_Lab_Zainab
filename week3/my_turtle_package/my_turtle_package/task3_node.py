import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from turtlesim.msg import Pose  
import math 

class GoToGoalNode(Node):
    def __init__(self):
        super().__init__('go_to_goal_node')
        
        # 1. PUBLISHER: Tells the turtle how to move
        self.publisher_ = self.create_publisher(Twist, 'turtle1/cmd_vel', 10)
        
        # 2. SUBSCRIBER: Listens to where the turtle currently is
        self.subscriber_ = self.create_subscription(Pose, 'turtle1/pose', self.update_pose, 10)
        
        self.pose = Pose() # Variable to store the current location
        
        # Define our Goal Location
        self.goal_x = 8.0
        self.goal_y = 8.0
        
        self.timer = self.create_timer(0.1, self.move_to_goal)

    def update_pose(self, data):
        # Every time the simulator broadcasts the turtle's location, this saves it!
        self.pose = data

    def move_to_goal(self):
        # Calculate how far away we are using the Pythagorean theorem
        distance_to_goal = math.sqrt((self.goal_x - self.pose.x)**2 + (self.goal_y - self.pose.y)**2)
        
        # Calculate the angle we need to point towards
        angle_to_goal = math.atan2(self.goal_y - self.pose.y, self.goal_x - self.pose.x)

        msg = Twist()

        if distance_to_goal >= 0.1:
            # If we are not there yet, keep driving and steering!
            msg.linear.x = 1.0 * distance_to_goal             # Slow down as we get closer
            msg.angular.z = 4.0 * (angle_to_goal - self.pose.theta) # Steer towards the goal
            self.publisher_.publish(msg)
        else:
            # We arrived! Stop the turtle.
            msg.linear.x = 0.0
            msg.angular.z = 0.0
            self.publisher_.publish(msg)
            
            # Print a success message to your terminal!
            self.get_logger().info("Target Location Reached!")
            self.timer.cancel() # Stop the loop

def main(args=None):
    rclpy.init(args=args)
    node = GoToGoalNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()