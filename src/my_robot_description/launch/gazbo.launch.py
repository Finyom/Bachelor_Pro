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
    urdf_file      = os.path.join(pkg_path, 'urdf', 'm_robot.xacro')
    world_file     = os.path.join(pkg_path, 'worlds', 'my_world.world')
    controllers_yaml = os.path.join(pkg_path, 'config', 'controllers.yaml')

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

    spawn_entity = Node(
        package='gazebo_ros',
        executable='spawn_entity.py',
        arguments=['-entity', 'm_robot', '-topic', 'robot_description'],
        output='screen'
    )

    controller_manager = Node(
        package='controller_manager',
        executable='ros2_control_node',
        parameters=[ controllers_yaml, sim_time_param],  # ← robot_description!
        output='screen'
    )

    # Spawner starten erst NACH joint_state_broadcaster
    joint_state_broadcaster_spawner = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['joint_state_broadcaster', '--controller-manager', '/controller_manager'],
    )

    diff_drive_spawner = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['diff_drive_base_controller', '--controller-manager', '/controller_manager'],
    )

    # diff_drive erst starten wenn joint_state_broadcaster fertig ist
    diff_drive_event = RegisterEventHandler(
        event_handler=OnProcessExit(
            target_action=joint_state_broadcaster_spawner,
            on_exit=[diff_drive_spawner]
        )
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
        spawn_entity,
        controller_manager,
        joint_state_broadcaster_spawner,
        diff_drive_event,           # ← diff_drive wartet auf broadcaster
        rtabmap,
    ])