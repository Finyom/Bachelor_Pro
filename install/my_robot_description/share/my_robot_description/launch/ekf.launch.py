from launch import LaunchDescription
from launch_ros.actions import Node
from launch.substitutions import PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare

def generate_launch_description():
    ekf_config = PathJoinSubstitution([
        FindPackageShare('my_robot_description'),
        'config',
        'ekf.yaml'
    ])

    return LaunchDescription([
        
        # EKF-Filter
        Node(
            package='robot_localization',
            executable='ekf_node',
            name='ekf_filter_node',
            output='screen',
            parameters=[
                ekf_config,
                {
                    'use_sim_time': True
                }
            ],
        
        ),

    
    ])