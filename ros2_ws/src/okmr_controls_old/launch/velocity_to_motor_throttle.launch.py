from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import ExecuteProcess
from ament_index_python.packages import get_package_share_directory
import os

def generate_launch_description():
    pid_config = os.path.join(
      get_package_share_directory('okmr_controls'), 
      'params',
      'pid.yaml'
    )

    return LaunchDescription([
        Node(
            package='okmr_controls',
            executable='pid',
            name='yaw_rate_pid_controller',
            remappings=[
                ('/PID/XXX/target', '/PID/yaw_rate/target'),
                ('/PID/XXX/actual', '/PID/yaw_rate/actual'),
                ('/PID_correction/XXX', '/PID_correction/yaw')
            ],
            parameters=[pid_config]
        ),
        Node(
            package='okmr_controls',
            executable='pid',
            name='pitch_rate_pid_controller',
            remappings=[
                ('/PID/XXX/target', '/PID/pitch_rate/target'),
                ('/PID/XXX/actual', '/PID/pitch_rate/actual'),
                ('/PID_correction/XXX', '/PID_correction/pitch')
            ],
            parameters=[pid_config]
        ),
        Node(
            package='okmr_controls',
            executable='pid',
            name='roll_rate_pid_controller',
            remappings=[
                ('/PID/XXX/target', '/PID/roll_rate/target'),
                ('/PID/XXX/actual', '/PID/roll_rate/actual'),
                ('/PID_correction/XXX', '/PID_correction/roll')
            ],
            parameters=[pid_config]
        ),
        Node(
            package='okmr_controls',
            executable='pid',
            name='surge_pid_controller',
            remappings=[
                ('/PID/XXX/target', '/PID/surge/target'),
                ('/PID/XXX/actual', '/PID/surge/actual'),
                ('/PID_correction/XXX', '/PID_correction/surge')
            ],
            parameters=[pid_config]
        ),
        Node(
            package='okmr_controls',
            executable='pid',
            name='sway_pid_controller',
            remappings=[
                ('/PID/XXX/target', '/PID/sway/target'),
                ('/PID/XXX/actual', '/PID/sway/actual'),
                ('/PID_correction/XXX', '/PID_correction/sway')
            ],
            parameters=[pid_config]
        ),
        Node(
            package='okmr_controls',
            executable='pid',
            name='heave_pid_controller',
            remappings=[
                ('/PID/XXX/target', '/PID/heave/target'),
                ('/PID/XXX/actual', '/PID/heave/actual'),
                ('/PID_correction/XXX', '/PID_correction/heave')
            ],
            parameters=[pid_config]),
        ])
