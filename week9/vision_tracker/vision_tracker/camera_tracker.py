import rclpy
from rclpy.node import Node

from sensor_msgs.msg import Image
from geometry_msgs.msg import Twist

from cv_bridge import CvBridge

import cv2
import numpy as np


class CameraTracker(Node):

    def __init__(self):
        super().__init__('camera_tracker')

        # Subscribe camera
        self.subscription = self.create_subscription(
            Image,
            '/camera/image_raw',
            self.image_callback,
            10
        )

        # Publish robot velocity
        self.publisher = self.create_publisher(Twist, '/cmd_vel', 10)

        self.bridge = CvBridge()

        # Tracking parameters
        # Tracking parameters
        self.kp_angular = 0.001      # Gentle rotation gain
        self.kd_angular = 0.0005
        self.max_turn = 0.3          # Reduced from 0.5 for smoother steering
        self.max_linear = 0.2
        self.search_speed = 0.3
        self.dead_zone = 50          # Larger dead zone with simultaneous motion

        self.min_area = 300          # was 500
        self.max_area = 200000       # Stop if too close
        self.min_linear = 0.08
        self.prev_error = 0
        
        # Fine alignment parameters
        self.alignment_threshold = 2  # Absolute error in pixels to consider aligned
        self.target_distance = 0.56   # Stop at 0.56m from centroid (0.06m from cylinder surface)
        
        # Distance estimation: distance = calibration_constant / sqrt(area)
        # Calibration: assumes typical robot camera with 0.5m radius cylinder
        self.distance_calibration = 500  # Tune this based on actual camera

        self.get_logger().info("Red Object Tracker Started")

    def image_callback(self, msg):

        frame = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')

        h, w, _ = frame.shape
        frame_center_x = w // 2

        # Convert to HSV
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        # Detect RED color
        lower_red1 = np.array([0, 120, 70])
        upper_red1 = np.array([10, 255, 255])

        lower_red2 = np.array([170, 120, 70])
        upper_red2 = np.array([180, 255, 255])

        mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
        mask2 = cv2.inRange(hsv, lower_red2, upper_red2)

        mask = mask1 + mask2

        # Remove noise
        kernel = np.ones((5, 5), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_DILATE, kernel)

        # Find contours
        contours, _ = cv2.findContours(
            mask,
            cv2.RETR_TREE,
            cv2.CHAIN_APPROX_SIMPLE
        )

        twist = Twist()

        if contours:

            largest = max(contours, key=cv2.contourArea)
            area = cv2.contourArea(largest)

            if area > self.min_area:

                M = cv2.moments(largest)

                if M["m00"] != 0:

                    cx = int(M["m10"] / M["m00"])
                    cy = int(M["m01"] / M["m00"])

                    # Error calculation
                    error = frame_center_x - cx
                    
                    # Estimate current distance from area
                    estimated_distance = self.distance_calibration / np.sqrt(max(area, 1))

                    # Fine alignment mode: if error is small, move straight toward cylinder
                    if abs(error) < self.alignment_threshold:
                        angular_speed = 0.0
                        
                        # Check if reached target distance
                        if estimated_distance <= self.target_distance:
                            linear_speed = 0.0
                        else:
                            linear_speed = 0.15
                    else:
                        # Coarse alignment: steering correction to center
                        d_error = error - self.prev_error
                        angular_speed = (self.kp_angular * error) + (self.kd_angular * d_error)
                        angular_speed = max(-self.max_turn, min(self.max_turn, angular_speed))
                        linear_speed = 0.0

                    self.prev_error = error

                    # Set robot velocity
                    twist.linear.x = float(linear_speed)
                    twist.angular.z = float(angular_speed)

                    # Draw visuals
                    cv2.drawContours(frame, [largest], -1, (0, 255, 0), 2)
                    cv2.circle(frame, (cx, cy), 7, (0, 0, 255), -1)

                    cv2.line(
                        frame,
                        (frame_center_x, 0),
                        (frame_center_x, h),
                        (255, 255, 255),
                        1
                    )

                    cv2.putText(
                        frame,
                        f'Error: {error}',
                        (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.7,
                        (0, 255, 0),
                        2
                    )

                    cv2.putText(
                        frame,
                        f'Area: {int(area)} / {self.max_area}',
                        (10, 70),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.7,
                        (0, 255, 0),
                        2
                    )

        else:
            # No object detected → keep searching
            twist.angular.z = self.search_speed
            self.prev_error = 0  # Reset error for next detection

        # Publish movement
        self.publisher.publish(twist)

        # Show windows
        cv2.imshow("Camera View", frame)
        cv2.imshow("Red Mask", mask)
        cv2.waitKey(1)


def main(args=None):

    rclpy.init(args=args)

    node = CameraTracker()

    rclpy.spin(node)

    node.destroy_node()

    rclpy.shutdown()


if __name__ == '__main__':
    main()