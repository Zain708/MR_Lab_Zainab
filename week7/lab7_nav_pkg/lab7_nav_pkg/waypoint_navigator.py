
import sys
import time

import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
from nav2_msgs.action import NavigateToPose
from geometry_msgs.msg import PoseStamped

# ---------------------------------------------------------------------------
# Configurable dwell time (seconds) at each waypoint
# ---------------------------------------------------------------------------
DWELL_SEC = 2.0


# ---------------------------------------------------------------------------
# Helper — build a PoseStamped for the 'map' frame
# ---------------------------------------------------------------------------
def make_pose(x: float, y: float, qz: float, qw: float) -> PoseStamped:
    """
    Create a PoseStamped message in the 'map' frame.

    Parameters
    ----------
    x, y   : position in metres
    qz     : orientation quaternion z component
    qw     : orientation quaternion w component
    """
    pose = PoseStamped()
    pose.header.frame_id = 'map'

    pose.pose.position.x = float(x)
    pose.pose.position.y = float(y)
    pose.pose.position.z = 0.0

    pose.pose.orientation.x = 0.0
    pose.pose.orientation.y = 0.0
    pose.pose.orientation.z = float(qz)
    pose.pose.orientation.w = float(qw)

    return pose


# ---------------------------------------------------------------------------
# Waypoint Navigator Node
# ---------------------------------------------------------------------------
class WaypointNavigator(Node):
    """
    ROS 2 node that navigates through a list of waypoints one by one using
    the NavigateToPose action server.  After reaching each waypoint the robot
    dwells for DWELL_SEC seconds before moving to the next goal.
    """

    def __init__(self):
        super().__init__('waypoint_navigator')
        self._client = ActionClient(self, NavigateToPose, 'navigate_to_pose')
        self.get_logger().info('WaypointNavigator node initialised.')

    # ------------------------------------------------------------------
    def navigate_to(self, pose: PoseStamped, index: int) -> bool:
        """
        Send a single NavigateToPose goal and block until reached.

        Returns True if the goal succeeded, False otherwise.
        """
        self.get_logger().info(
            f'[WP{index}] Waiting for navigate_to_pose server...')
        self._client.wait_for_server()

        goal_msg = NavigateToPose.Goal()
        goal_msg.pose = pose

        self.get_logger().info(
            f'[WP{index}] Navigating to  x={pose.pose.position.x:.3f}  '
            f'y={pose.pose.position.y:.3f}')

        # Send goal -------------------------------------------------------
        send_future = self._client.send_goal_async(
            goal_msg,
            feedback_callback=lambda fb: self._feedback_cb(fb, index)
        )
        rclpy.spin_until_future_complete(self, send_future)
        goal_handle = send_future.result()

        if not goal_handle.accepted:
            self.get_logger().error(f'[WP{index}] Goal REJECTED!')
            return False

        self.get_logger().info(f'[WP{index}] Goal ACCEPTED — navigating...')

        # Wait for result -------------------------------------------------
        result_future = goal_handle.get_result_async()
        rclpy.spin_until_future_complete(self, result_future)

        status = result_future.result().status
        if status == 4:   # SUCCEEDED
            self.get_logger().info(f'[WP{index}]  REACHED!')
            return True
        else:
            self.get_logger().warn(
                f'[WP{index}]  Navigation ended with status={status}')
            return False

    # ------------------------------------------------------------------
    def _feedback_cb(self, feedback_msg, index: int) -> None:
        """Log distance remaining during navigation."""
        fb = feedback_msg.feedback
        dist = getattr(fb, 'distance_remaining', '?')
        self.get_logger().info(
            f'[WP{index}] Distance remaining: {dist:.2f} m'
            if isinstance(dist, float) else f'[WP{index}] Navigating...')

    # ------------------------------------------------------------------
    def run_mission(self, waypoints: list) -> None:
        """Iterate through waypoints, dwell DWELL_SEC at each one."""
        total = len(waypoints)
        self.get_logger().info(
            f'\n'
            f'============================================================\n'
            f' Lab 7 — Task 2: Multi-Waypoint Mission\n'
            f' Total waypoints : {total}\n'
            f' Dwell time      : {DWELL_SEC} s per waypoint\n'
            f'============================================================'
        )

        for i, pose in enumerate(waypoints, start=1):
            success = self.navigate_to(pose, i)

            if success:
                self.get_logger().info(
                    f'[WP{i}/{total}]   Dwelling for {DWELL_SEC} s...')
                time.sleep(DWELL_SEC)
                self.get_logger().info(
                    f'[WP{i}/{total}] ▶  Resuming — moving to next waypoint.')
            else:
                self.get_logger().warn(
                    f'[WP{i}/{total}] Skipping dwell (goal not reached).')

        self.get_logger().info(
            '============================================================\n'
            ' Mission COMPLETE — all waypoints processed.\n'
            '============================================================'
        )


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main(args=None):
    rclpy.init(args=args)
    navigator = WaypointNavigator()

    # ------------------------------------------------------------------
    # Task 3: Dynamic Waypoint Injection
    #
    # If CLI arguments are provided, parse them as groups of 3 floats:
    #   x   y   orientation_w
    # qz is set to 0.0 for simple forward-facing heading.
    #
    # Example:
    #   python3 waypoint_navigator.py 0.5 0.0 1.0  1.0 0.5 1.0  0.0 0.0 1.0
    # ------------------------------------------------------------------
    cli_args = sys.argv[1:]  # strip the script/node name

    if cli_args:
        # ---- Parse CLI waypoints ----------------------------------------
        if len(cli_args) % 3 != 0:
            navigator.get_logger().error(
                f'ERROR: Expected groups of 3 values (x y orientation_w), '
                f'but got {len(cli_args)} argument(s). Exiting.')
            navigator.destroy_node()
            rclpy.shutdown()
            return

        try:
            values = [float(v) for v in cli_args]
        except ValueError as e:
            navigator.get_logger().error(
                f'ERROR: Non-numeric argument detected — {e}. Exiting.')
            navigator.destroy_node()
            rclpy.shutdown()
            return

        waypoints = []
        for i in range(0, len(values), 3):
            x, y, qw = values[i], values[i + 1], values[i + 2]
            waypoints.append(make_pose(x, y, qz=0.0, qw=qw))

        navigator.get_logger().info(
            f'Task 3 — {len(waypoints)} waypoint(s) loaded from CLI arguments.')

    else:
        # ---- Fall back to Task 2 hardcoded mission -----------------------
        navigator.get_logger().info(
            'No CLI args detected — running Task 2 hardcoded mission.')
        waypoints = [
            make_pose( 1.1967625197963416, -1.2706972530922527,
                      -0.15014407314668224,  0.9886641276484769),  # WP1
            make_pose( 2.769741315065822,  -1.1817082171672006,
                       0.1642831504439697,   0.9864132229852781),  # WP2
            make_pose( 3.7372927864786107, -0.46738096284809677,
                       0.602541734060909,    0.7980873753636708),  # WP3
            make_pose( 3.801827042054849,   0.2669668235261615,
                       0.6738942629474801,   0.7388278029192408),  # WP4
            make_pose( 2.6935585403082056,  2.480706811584958,
                       0.9907032565516748,   0.13604064634478366), # WP5
        ]

    navigator.run_mission(waypoints)
    navigator.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
