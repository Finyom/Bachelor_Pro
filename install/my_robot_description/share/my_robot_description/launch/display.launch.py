import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node
from launch.substitutions import Command
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.parameter_descriptions import ParameterValue

def generate_launch_description():
    # Pfad zur Xacro-Datei
    pkg_dir = get_package_share_directory('my_robot_description')
    urdf_file = os.path.join(pkg_dir, 'urdf', 'm_robot.xacro')
    rviz_config = os.path.join(pkg_dir, 'rviz', 'robot.rviz')
    
    # Xacro zu URDF konvertieren

    robot_description_content = ParameterValue(
        Command(['xacro ', urdf_file]),
        value_type=str
    )
    robot_description_content = Command(['xacro ', urdf_file])
    
    return LaunchDescription([
        # Robot State Publisher
        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            name='robot_state_publisher',
            parameters=[{'robot_description': robot_description_content},{'use_sim_time': True}],
            output="screen"
        ),
        
        # Joint State Publisher GUI
        Node(
            package='joint_state_publisher_gui',
            executable='joint_state_publisher_gui',
            name='joint_state_publisher_gui',
            output="screen"
        ),
        
        # RViz
        Node(
            package='rviz2',
            executable='rviz2',
            name='rviz2',
            output='screen',
            arguments=['-d', str(rviz_config)],
            parameters=[{'use_sim_time': True}]
        )
    ])