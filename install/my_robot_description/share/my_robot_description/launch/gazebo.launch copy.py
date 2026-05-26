from launch import LaunchDescription
from launch.actions import (DeclareLaunchArgument, ExecuteProcess,
                             RegisterEventHandler, TimerAction)
from launch.event_handlers import OnProcessExit
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution, Command
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare
from launch_ros.parameter_descriptions import ParameterValue
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
import os

def generate_launch_description():

    use_sim_time = DeclareLaunchArgument(
        'use_sim_time',
        default_value='true',
        description='Use simulation clock if true'
    )

    pkg_path = FindPackageShare('my_robot_description').find('my_robot_description')
    urdf_file      = os.path.join(pkg_path, 'urdf', 'm_robot.urdf')
    world_file     = os.path.join(pkg_path, 'worlds', 'my_world.world')
    #controllers_yaml = os.path.join(pkg_path, 'config', 'controllers.yaml')

    robot_description_content = ParameterValue(
        Command(['xacro ', urdf_file]),
        value_type=str
    )
    robot_description = {'robot_description': robot_description_content}
    sim_time_param  = {'use_sim_time': LaunchConfiguration('use_sim_time')}

    # ── Nodes ──────────────────────────────────────────────

    gazebo = ExecuteProcess(
        cmd=['gazebo', '--verbose', '-s', 'libgazebo_ros_factory.so', world_file],
        output='screen'
    )

    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        parameters=[robot_description, sim_time_param]
    )

    joint_state_publisher = Node(
            package='joint_state_publisher',
            executable='joint_state_publisher',
            name='joint_state_publisher',
            output="screen"
    ),

    spawn_entity = Node(
        package='gazebo_ros',
        executable='spawn_entity.py',
        arguments=['-entity', 'm_robot', '-topic', 'robot_description'],
        output='screen'
    )


    rtabmap = TimerAction(
        period=3.0,
        actions=[
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource([
                    PathJoinSubstitution([
                        FindPackageShare('my_robot_description'),
                        'launch',
                        'rtabmap.launch.py'
                    ])
                ])
            )
        ]
    )

    return LaunchDescription([
        use_sim_time,
        gazebo,
        robot_state_publisher,
        spawn_entity,           # ← diff_drive wartet auf broadcaster
        joint_state_publisher,
        rtabmap,
    ])