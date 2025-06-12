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
            name='yaw_angle_pid_controller',
            remappings=[
                ('/PID/XXX/target', '/PID/yaw/target'), 
                ('/PID/XXX/actual', '/PID/yaw/actual'),
                ('/PID_correction/XXX', '/PID/yaw_rate/target')#cascading
            ],
            parameters=[pid_config]
        ),
        Node(
            package='okmr_controls',
            executable='pid',
            name='pitch_angle_pid_controller',
            remappings=[
                ('/PID/XXX/target', '/PID/pitch/target'), 
                ('/PID/XXX/actual', '/PID/pitch/actual'),
                ('/PID_correction/XXX', '/PID/pitch_rate/target')#cascading
            ],
            parameters=[pid_config]
        ),
        Node(
            package='okmr_controls',
            executable='pid',
            name='roll_angle_pid_controller',
            remappings=[
                ('/PID/XXX/target', '/PID/roll/target'), 
                ('/PID/XXX/actual', '/PID/roll/actual'),
                ('/PID_correction/XXX', '/PID/roll_rate/target')#cascading
            ],
            parameters=[pid_config]
        ),
        Node(
            package='okmr_controls',
            executable='pid',
            name='x_translation_pid_controller',
            remappings=[
                ('/PID/XXX/target', '/PID/zero_reference/target'), 
                ('/PID/XXX/actual', '/PID/x_translation/actual'),
                ('/PID_correction/XXX', '/PID/surge/target')#cascading
            ],
            parameters=[pid_config]
        ),
        Node(
            package='okmr_controls',
            executable='pid',
            name='y_translation_pid_controller',
            remappings=[
                ('/PID/XXX/target', '/PID/zero_reference/target'),
                ('/PID/XXX/actual', '/PID/y_translation/actual'),
                ('/PID_correction/XXX', '/PID/sway/target')#cascading
            ],
            parameters=[pid_config]
        ),
        Node(
            package='okmr_controls',
            executable='pid',
            name='z_translation_pid_controller',
            remappings=[
                ('/PID/XXX/target', '/PID/zero_reference/target'),
                ('/PID/XXX/actual', '/PID/z_translation/actual'),
                ('/PID_correction/XXX', '/PID/heave/target')#cascading
            ],
            parameters=[pid_config]
        )])

