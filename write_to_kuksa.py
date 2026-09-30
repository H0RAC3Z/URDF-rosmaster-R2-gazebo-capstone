#!/usr/bin/env python3
"""Forward the ROS vehicle state topics to Eclipse KUKSA Databroker."""

import os

import rclpy
from rclpy.node import Node
from std_msgs.msg import Float64
from kuksa_client.grpc import Datapoint, VSSClient


class KuksaWriter(Node):
    """Write ROS vehicle speed and steering angle to VSS datapoints."""

    def __init__(self, kuksa_client):
        super().__init__("write_to_kuksa")
        # VSSClient owns a synchronous gRPC channel. Use it directly in the
        # callbacks so each topic update is immediately forwarded to KUKSA.
        self.kuksa = kuksa_client
        self.create_subscription(
            Float64, "/vehicle/speed_mps", self.speed_callback, 10
        )
        self.create_subscription(
            Float64,
            "/vehicle/steering_angle_rad",
            self.steering_callback,
            10,
        )
        self.get_logger().info("Forwarding vehicle state topics to KUKSA Databroker")

    def speed_callback(self, msg: Float64):
        # VSS Vehicle.Speed is defined in km/h; the ROS topic is in m/s.
        self._write("Vehicle.Speed", msg.data * 3.6)

    def steering_callback(self, msg: Float64):
        self._write("Vehicle.SteeringAngle", msg.data)

    def _write(self, path: str, value: float):
        try:
            self.kuksa.set_current_values({path: Datapoint(float(value))})
        except Exception as exc:  # Keep the ROS node alive if a write fails.
            self.get_logger().error(f"Failed to write {path}={value} to KUKSA: {exc}")


def main():
    host = os.getenv("KUKSA_HOST", "127.0.0.1")
    port = int(os.getenv("KUKSA_PORT", "55555"))
    token = os.getenv("KUKSA_TOKEN")
    rclpy.init()
    node = None
    try:
        # The SDK context manager closes the gRPC channel on shutdown.
        with VSSClient(host, port, token=token) as kuksa_client:
            node = KuksaWriter(kuksa_client)
            rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        if node is not None:
            node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
