from launch import LaunchDescription
from launch_ros.actions import Node
from launch.substitutions import PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare

def generate_launch_description():
    slam_config = PathJoinSubstitution([
        FindPackageShare('my_robot_description'),
        'config',
        'mapper_params_online_async.yaml'
    ])

    return LaunchDescription([
        Node(
            package='slam_toolbox',
            executable='async_slam_toolbox_node',
            name='slam_toolbox',
            output='screen',
            parameters=[
                slam_config,
                {
                    'use_sim_time': True,
                    'odom_topic': '/odometry/filtered',  # ← EKF Output!
                }
            ]
        )
    ])