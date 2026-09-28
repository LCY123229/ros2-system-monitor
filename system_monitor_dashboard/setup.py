from setuptools import setup

package_name = 'system_monitor_dashboard'

setup(
    name=package_name,
    version='0.1.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='System Monitor Maintainers',
    maintainer_email='maintainer@localhost',
    description='System status publisher and PyQt5 dashboard for ROS 2 Humble.',
    license='Apache-2.0',
    entry_points={
        'console_scripts': [
            'status_publisher = system_monitor_dashboard.publisher:main',
            'status_dashboard = system_monitor_dashboard.dashboard:main',
        ],
    },
)
