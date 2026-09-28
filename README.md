# ROS 2 系统状态监控

适用于 Ubuntu 22.04 + ROS 2 Humble 的双包示例。`system_monitor_interfaces` 定义状态消息；`system_monitor_dashboard` 提供每秒采样的发布节点和 PyQt5 窗口。发布节点可以单独运行在被监控主机上，窗口可以运行在同一 ROS 2 网络中的另一台主机上。

## 消息和数据含义

话题：`/system_status`；类型：`system_monitor_interfaces/msg/SystemStatus`。

| 字段 | 含义 |
| --- | --- |
| `stamp` | 采样时的系统时间，ROS `builtin_interfaces/Time` |
| `hostname` | 被监控主机名 |
| `cpu_percent` | 自上一次采样以来的整体 CPU 使用率，百分比 |
| `memory_percent` | 物理内存使用率，百分比 |
| `memory_total_bytes` | 物理内存总量，字节 |
| `memory_available_bytes` | 可供新进程使用的内存，字节 |
| `network_rx_bytes` | 系统启动以来所有网卡累计接收量，字节 |
| `network_tx_bytes` | 系统启动以来所有网卡累计发送量，字节 |

网络数值是累计值，不是瞬时速率。`psutil` 的 available 内存指标代表可用内存，通常比 Linux 的 free 字段更适合反映剩余可用容量。窗口会在 3 秒没有收到新消息时显示连接中断。

## 安装和构建

在 Ubuntu 22.04、已安装 ROS 2 Humble 的终端执行：

```bash
sudo apt update
sudo apt install python3-psutil python3-pyqt5 python3-colcon-common-extensions
mkdir -p ~/ros2_ws/src
cd ~/ros2_ws/src
git clone https://github.com/LCY123229/ros2-system-monitor.git
cd ~/ros2_ws
source /opt/ros/humble/setup.bash
colcon build --packages-up-to system_monitor_dashboard
source install/setup.bash
```

如从压缩包获得源码，将压缩包中的两个包目录复制到 `~/ros2_ws/src/` 也可以。桌面端必须有图形会话（`DISPLAY` 或 Wayland），不要用 `sudo ros2 run` 启动窗口。

## 运行

终端 1：

```bash
source /opt/ros/humble/setup.bash
source ~/ros2_ws/install/setup.bash
ros2 run system_monitor_dashboard status_publisher
```

终端 2：

```bash
source /opt/ros/humble/setup.bash
source ~/ros2_ws/install/setup.bash
ros2 run system_monitor_dashboard status_dashboard
```

也可运行 `ros2 topic echo /system_status` 查看原始消息。两台机器运行时，确保 ROS 2 网络可互相发现，且 `ROS_DOMAIN_ID` 相同。

## 验收

1. `ros2 interface show system_monitor_interfaces/msg/SystemStatus` 可显示全部字段。
2. 发布节点启动后，`ros2 topic hz /system_status` 约为 1 Hz。
3. 窗口显示时间、主机名、CPU、内存和网络收发量；停止发布节点 3 秒后窗口显示“连接中断”。

本项目使用 Apache-2.0 许可。发布 GitHub 前，可按需要更新两个 `package.xml` 中的维护者信息。
