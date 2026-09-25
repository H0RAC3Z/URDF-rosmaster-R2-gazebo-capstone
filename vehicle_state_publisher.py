#!/usr/bin/env python3
"""vehicle_state_publisher.py

Subscribes to /joint_states (as bridged from Gazebo) and republishes two
simple, KUKSA-friendly scalar topics:

    /vehicle/speed_mps           std_msgs/Float64   (average driven-wheel linear speed, m/s)
    /vehicle/steering_angle_rad  std_msgs/Float64   (average front steering angle, rad; +left)

Rationale: /joint_states gives raw per-joint position/velocity for all six
joints, which is fine for debugging but not what a downstream consumer
(KUKSA, logging, a dashboard) wants to parse. This node does the one bit of
math joint_states doesn't give you for free -- wheel angular velocity (rad/s)
-> linear speed (m/s) -- and averages the two driven/steered wheels so a
consumer gets one clean number for each.

Run (with Gazebo + bridge already running):
    ros2 run --prefix 'python3' rclpy vehicle_state_publisher.py   # not how ros2 run works, see below
    python3 vehicle_state_publisher.py                             # simplest: just run it directly

No package/build step is required to just run this directly with rclpy
installed (it is, inside the ROS 2 Humble container).
"""
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState
from std_msgs.msg import Float64

WHEEL_RADIUS = 0.0345  # m, measured from mesh bounding box
DRIVEN_WHEEL_JOINTS = ["back_left_joint", "back_right_joint"]
STEER_JOINTS = ["front_left_steer_joint", "front_right_steer_joint"]


class VehicleStatePublisher(Node):
    def __init__(self):
        super().__init__("vehicle_state_publisher")
        self.sub = self.create_subscription(JointState, "/joint_states", self.cb, 10)
        self.speed_pub = self.create_publisher(Float64, "/vehicle/speed_mps", 10)
        self.steer_pub = self.create_publisher(Float64, "/vehicle/steering_angle_rad", 10)
        self._warned_missing = set()

    def cb(self, msg: JointState):
        idx = {name: i for i, name in enumerate(msg.name)}

        speeds = []
        for j in DRIVEN_WHEEL_JOINTS:
            if j in idx and idx[j] < len(msg.velocity):
                speeds.append(msg.velocity[idx[j]] * WHEEL_RADIUS)
            elif j not in self._warned_missing:
                self.get_logger().warn(f"joint '{j}' not in /joint_states or has no velocity field")
                self._warned_missing.add(j)

        angles = []
        for j in STEER_JOINTS:
            if j in idx and idx[j] < len(msg.position):
                angles.append(msg.position[idx[j]])
            elif j not in self._warned_missing:
                self.get_logger().warn(f"joint '{j}' not in /joint_states or has no position field")
                self._warned_missing.add(j)

        if speeds:
            self.speed_pub.publish(Float64(data=sum(speeds) / len(speeds)))
        if angles:
            self.steer_pub.publish(Float64(data=sum(angles) / len(angles)))


def main():
    rclpy.init()
    node = VehicleStatePublisher()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
