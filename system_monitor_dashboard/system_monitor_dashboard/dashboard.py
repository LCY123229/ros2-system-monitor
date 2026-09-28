"""Display ROS 2 system status messages in a compact Qt window."""

import signal
import sys
import time
from datetime import datetime

import rclpy
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtWidgets import QApplication, QFormLayout, QLabel, QWidget
from rclpy.node import Node

from system_monitor_interfaces.msg import SystemStatus


def format_bytes(value):
    """Format a byte count in binary units, keeping byte precision for small values."""
    value = float(value)
    for unit in ('B', 'KiB', 'MiB', 'GiB', 'TiB', 'PiB'):
        if value < 1024.0 or unit == 'PiB':
            return f'{value:.0f} {unit}' if unit == 'B' else f'{value:.2f} {unit}'
        value /= 1024.0


class StatusWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('ROS 2 系统状态监控')
        self.setMinimumWidth(390)
        self._fields = {}
        layout = QFormLayout(self)
        for key, caption in (
            ('stamp', '记录时间'),
            ('hostname', '主机名'),
            ('cpu', 'CPU 使用率'),
            ('memory', '内存使用率'),
            ('total', '内存总大小'),
            ('available', '剩余可用内存'),
            ('rx', '网络累计接收'),
            ('tx', '网络累计发送'),
            ('connection', '连接状态'),
        ):
            label = QLabel('—' if key != 'connection' else '等待数据')
            label.setTextInteractionFlags(Qt.TextSelectableByMouse)
            layout.addRow(caption, label)
            self._fields[key] = label
        self._last_received = None

    def display_status(self, message):
        stamp = message.stamp.sec + message.stamp.nanosec / 1_000_000_000
        self._fields['stamp'].setText(datetime.fromtimestamp(stamp).strftime('%Y-%m-%d %H:%M:%S'))
        self._fields['hostname'].setText(message.hostname)
        self._fields['cpu'].setText(f'{message.cpu_percent:.1f} %')
        self._fields['memory'].setText(f'{message.memory_percent:.1f} %')
        self._fields['total'].setText(format_bytes(message.memory_total_bytes))
        self._fields['available'].setText(format_bytes(message.memory_available_bytes))
        self._fields['rx'].setText(format_bytes(message.network_rx_bytes))
        self._fields['tx'].setText(format_bytes(message.network_tx_bytes))
        self._last_received = time.monotonic()
        self._fields['connection'].setText('已连接')

    def update_connection(self):
        if self._last_received is not None and time.monotonic() - self._last_received > 3:
            self._fields['connection'].setText('连接中断')


class StatusSubscriber(Node):
    def __init__(self, window):
        super().__init__('system_status_dashboard')
        self._subscription = self.create_subscription(
            SystemStatus, 'system_status', window.display_status, 10
        )


def main(args=None):
    app = QApplication([sys.argv[0]])
    rclpy.init(args=args)
    window = StatusWindow()
    node = StatusSubscriber(window)
    timer = QTimer()

    def poll_status():
        if not rclpy.ok():
            timer.stop()
            app.quit()
            return
        rclpy.spin_once(node, timeout_sec=0)
        window.update_connection()

    def request_shutdown(_signum, _frame):
        timer.stop()
        app.quit()

    previous_handlers = {
        sig: signal.getsignal(sig) for sig in (signal.SIGINT, signal.SIGTERM)
    }
    for sig in previous_handlers:
        signal.signal(sig, request_shutdown)

    timer.timeout.connect(poll_status)
    timer.start(100)
    window.show()
    try:
        return app.exec_()
    finally:
        timer.stop()
        for sig, previous_handler in previous_handlers.items():
            signal.signal(sig, previous_handler)
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    sys.exit(main())
