#!/usr/bin/env python3

import rclpy
from rclpy.node import Node

from sensor_msgs.msg import Image
from geometry_msgs.msg import Twist

from cv_bridge import CvBridge

import cv2
import numpy as np


class MultiColorTracker(Node):

    def __init__(self):

        super().__init__('multi_color_tracker')

        # Subscribe camera
        self.subscription = self.create_subscription(
            Image,
            '/camera/image_raw',
            self.image_callback,
            10
        )

        # Publish robot velocity
        self.publisher = self.create_publisher(
            Twist,
            '/cmd_vel',
            10
        )

        self.bridge = CvBridge()

        # ---------------------------------------------------
        # Control parameters
        # ---------------------------------------------------

        self.kp_angular = 0.002
        self.max_turn = 0.4

        self.forward_speed = 0.15
        self.backward_speed = -0.15
        self.right_turn_speed = -0.3

        self.search_speed = 0.2

        # Minimum contour area to be considered a valid detection
        self.min_area = 800

        # ---------------------------------------------------
        # Safe stopping parameters
        # ---------------------------------------------------

        self.target_distance = 0.56

        # Tune this for your camera / object size
        self.distance_calibration = 500

        # ---------------------------------------------------
        # Priority order: BLUE (0) > GREEN (1) > RED (2)
        # BLUE  → forward
        # GREEN → backward
        # RED   → turn right
        # ---------------------------------------------------
        self.priority_order = ["BLUE", "GREEN", "RED"]
        self.locked_color = None

        self.get_logger().info("Multi Color Tracker Started — Priority: BLUE > GREEN > RED")

    # ---------------------------------------------------
    # Find largest contour above min_area threshold
    # ---------------------------------------------------

    def get_largest_contour(self, mask):

        contours, _ = cv2.findContours(
            mask,
            cv2.RETR_TREE,
            cv2.CHAIN_APPROX_SIMPLE
        )

        if contours:

            largest = max(contours, key=cv2.contourArea)
            area = cv2.contourArea(largest)

            if area > self.min_area:
                return largest, area

        return None, 0

    # ---------------------------------------------------
    # Build color masks
    # ---------------------------------------------------

    def build_masks(self, hsv):

        kernel = np.ones((5, 5), np.uint8)

        # ---------------------------------------------------
        # RED MASK
        # Red wraps around 0/180 in HSV — use bitwise_or (NOT +)
        # to avoid uint8 overflow corruption.
        # ---------------------------------------------------

        lower_red1 = np.array([0,   100,  60])
        upper_red1 = np.array([10,  255, 255])

        lower_red2 = np.array([160, 100,  60])
        upper_red2 = np.array([180, 255, 255])

        red_mask = cv2.bitwise_or(
            cv2.inRange(hsv, lower_red1, upper_red1),
            cv2.inRange(hsv, lower_red2, upper_red2)
        )

        # ---------------------------------------------------
        # BLUE MASK
        # ---------------------------------------------------

        lower_blue = np.array([95,  120,  50])
        upper_blue = np.array([135, 255, 255])

        blue_mask = cv2.inRange(hsv, lower_blue, upper_blue)

        # ---------------------------------------------------
        # GREEN MASK
        # ---------------------------------------------------

        lower_green = np.array([35,  60,  60])
        upper_green = np.array([85, 255, 255])

        green_mask = cv2.inRange(hsv, lower_green, upper_green)

        # ---------------------------------------------------
        # Morphological cleaning (remove noise, fill gaps)
        # ---------------------------------------------------

        red_mask   = cv2.morphologyEx(red_mask,   cv2.MORPH_OPEN,  kernel)
        red_mask   = cv2.morphologyEx(red_mask,   cv2.MORPH_CLOSE, kernel)

        blue_mask  = cv2.morphologyEx(blue_mask,  cv2.MORPH_OPEN,  kernel)
        blue_mask  = cv2.morphologyEx(blue_mask,  cv2.MORPH_CLOSE, kernel)

        green_mask = cv2.morphologyEx(green_mask, cv2.MORPH_OPEN,  kernel)
        green_mask = cv2.morphologyEx(green_mask, cv2.MORPH_CLOSE, kernel)

        return red_mask, blue_mask, green_mask

    # ---------------------------------------------------
    # Strict priority selection
    # ---------------------------------------------------

    def select_target(self, red_contour, blue_contour, green_contour):
        """
        Always returns the highest-priority detected color.
        Priority: BLUE > GREEN > RED  (hard-coded, deterministic).
        """

        detected = {}

        if blue_contour  is not None: detected["BLUE"]  = blue_contour
        if green_contour is not None: detected["GREEN"] = green_contour
        if red_contour   is not None: detected["RED"]   = red_contour

        for color in self.priority_order:
            if color in detected:
                self.locked_color = color
                return color, detected[color]

        self.locked_color = None
        return None, None

    # ---------------------------------------------------
    # Image callback
    # ---------------------------------------------------

    def image_callback(self, msg):

        frame = self.bridge.imgmsg_to_cv2(
            msg,
            desired_encoding='bgr8'
        )

        h, w, _ = frame.shape
        frame_center_x = w // 2

        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        red_mask, blue_mask, green_mask = self.build_masks(hsv)

        red_contour,   red_area   = self.get_largest_contour(red_mask)
        blue_contour,  blue_area  = self.get_largest_contour(blue_mask)
        green_contour, green_area = self.get_largest_contour(green_mask)

        # ---------------------------------------------------
        # Strict priority selection: BLUE > GREEN > RED
        # ---------------------------------------------------

        selected_color, selected_contour = self.select_target(
            red_contour,
            blue_contour,
            green_contour
        )

        # ---------------------------------------------------
        # Robot control
        # ---------------------------------------------------

        twist = Twist()

        if selected_contour is not None:

            M = cv2.moments(selected_contour)

            if M["m00"] != 0:

                cx = int(M["m10"] / M["m00"])
                cy = int(M["m01"] / M["m00"])

                error = frame_center_x - cx

                angular_speed = self.kp_angular * error
                angular_speed = max(
                    -self.max_turn,
                    min(self.max_turn, angular_speed)
                )

                area = cv2.contourArea(selected_contour)
                estimated_distance = (
                    self.distance_calibration /
                    np.sqrt(max(area, 1))
                )

                # ---------------------------------------------------
                # BLUE → Move Forward (highest priority)
                # ---------------------------------------------------

                if selected_color == "BLUE":

                    if estimated_distance <= self.target_distance:
                        twist.linear.x = 0.0
                        twist.angular.z = 0.0
                    else:
                        twist.linear.x = self.forward_speed
                        twist.angular.z = angular_speed

                # ---------------------------------------------------
                # GREEN → Move Backward (second priority)
                # ---------------------------------------------------

                elif selected_color == "GREEN":

                    if estimated_distance <= self.target_distance:
                        twist.linear.x = 0.0
                        twist.angular.z = 0.0
                    else:
                        twist.linear.x = self.backward_speed
                        twist.angular.z = angular_speed

                # ---------------------------------------------------
                # RED → Turn Right (lowest priority)
                # ---------------------------------------------------

                elif selected_color == "RED":

                    twist.linear.x = 0.0
                    twist.angular.z = self.right_turn_speed

                # ---------------------------------------------------
                # Draw visuals
                # ---------------------------------------------------

                color_bgr = {
                    "BLUE":  (255, 0,   0),
                    "GREEN": (0,   255, 0),
                    "RED":   (0,   0,   255),
                }

                draw_color = color_bgr.get(selected_color, (255, 255, 255))

                cv2.drawContours(frame, [selected_contour], -1, draw_color, 2)

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
                    f'Target: {selected_color}',
                    (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.8,
                    draw_color,
                    2
                )

                cv2.putText(
                    frame,
                    f'Error: {error}  Dist: {estimated_distance:.2f}m',
                    (10, 65),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (200, 200, 200),
                    2
                )

                cv2.putText(
                    frame,
                    'Priority: BLUE > GREEN > RED',
                    (10, h - 10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    (180, 180, 180),
                    1
                )

        else:

            # No object detected → spin to search
            twist.angular.z = self.search_speed

            cv2.putText(
                frame,
                'Searching...',
                (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (0, 0, 255),
                2
            )

        # ---------------------------------------------------
        # Publish velocity
        # ---------------------------------------------------

        self.publisher.publish(twist)

        # ---------------------------------------------------
        # Show debug windows
        # ---------------------------------------------------

        cv2.imshow("Camera View", frame)
        cv2.imshow("Blue Mask",  blue_mask)
        cv2.imshow("Green Mask", green_mask)
        cv2.imshow("Red Mask",   red_mask)

        cv2.waitKey(1)


# ---------------------------------------------------
# Main
# ---------------------------------------------------

def main(args=None):

    rclpy.init(args=args)

    node = MultiColorTracker()

    rclpy.spin(node)

    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()