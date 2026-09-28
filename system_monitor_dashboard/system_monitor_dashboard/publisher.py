"""Publish system measurements once a second."""

import socket
import time

import psutil
import rclpy
from rclpy.node import Node

from system_monitor_interfaces.msg import SystemStatus


class StatusPublisher(Node):
    def __init__(self):
        super().__init__('system_status_publisher')
        self._publisher = self.create_publisher(SystemStatus, 'system_status', 10)
        self._hostname = socket.gethostname()
        psutil.cpu_percent(interval=None)  # Prime the non-blocking CPU sampler.
        self._timer = self.create_timer(1.0, self._publish_status)

    def _publish_status(self):
        sampled_at_ns = time.time_ns()
        memory = psutil.virtual_memory()
        network = psutil.net_io_counters()

        message = SystemStatus()
        message.stamp.sec, message.stamp.nanosec = divmod(sampled_at_ns, 1_000_000_000)
        message.hostname = self._hostname
        message.cpu_percent = float(psutil.cpu_percent(interval=None))
        message.memory_percent = float(memory.percent)
        message.memory_total_bytes = int(memory.total)
        message.memory_available_bytes = int(memory.available)
        message.network_rx_bytes = int(network.bytes_recv) if network else 0
        message.network_tx_bytes = int(network.bytes_sent) if network else 0
        self._publisher.publish(message)


def main(args=None):
    rclpy.init(args=args)
    node = StatusPublisher()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
