import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from turtlesim.msg import Pose
import math

class FollowLeaderNode(Node):
    def __init__(self):
        super().__init__('follow_the_leader')
        
        # Publisher to drive turtle2
        self.publisher_ = self.create_publisher(Twist, 'turtle2/cmd_vel', 10)
        
        # Subscribers to find out where BOTH turtles currently are
        self.sub_turtle1_ = self.create_subscription(Pose, 'turtle1/pose', self.update_pose1, 10)
        self.sub_turtle2_ = self.create_subscription(Pose, 'turtle2/pose', self.update_pose2, 10)
        
        self.pose1 = Pose() # Leader
        self.pose2 = Pose() # Follower
        self.timer = self.create_timer(0.1, self.follow_logic)

    def update_pose1(self, data):
        self.pose1 = data

    def update_pose2(self, data):
        self.pose2 = data

    def follow_logic(self):
        # Calculate the distance between turtle2 and turtle1
        distance = math.sqrt((self.pose1.x - self.pose2.x)**2 + (self.pose1.y - self.pose2.y)**2)
        
        msg = Twist()
        
        # If the follower is more than 0.5 meters away, chase the leader!
        if distance > 0.5: 
            angle_to_goal = math.atan2(self.pose1.y - self.pose2.y, self.pose1.x - self.pose2.x)
            
            angle_diff = angle_to_goal - self.pose2.theta
            # Normalize angle to be between -pi and pi
            while angle_diff > math.pi: angle_diff -= 2*math.pi
            while angle_diff < -math.pi: angle_diff += 2*math.pi
            
            msg.linear.x = 1.5 * distance      # Drive faster if far away
            msg.angular.z = 4.0 * angle_diff   # Steer towards the leader
        else:
            # We caught up! Stop so we don't crash.
            msg.linear.x = 0.0
            msg.angular.z = 0.0
            
        self.publisher_.publish(msg)

def main(args=None):
    rclpy.init(args=args)
    node = FollowLeaderNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
