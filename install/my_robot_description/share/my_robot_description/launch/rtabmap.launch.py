from launch import LaunchDescription
from launch_ros.actions import Node
from launch.substitutions import PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare

def generate_launch_description():

    rtabmap_config = PathJoinSubstitution([
        FindPackageShare('my_robot_description'),
        'config',
        'rtabmap.yaml'
    ])

    return LaunchDescription([

        # RTAB-Map Visual Odometry
        Node(
            package='rtabmap_odom',
            executable='rgbd_odometry',
            name='rgbd_odometry',
            output='screen',
            parameters=[rtabmap_config],
            remappings=[
                ('rgb/image',       '/camera/image_raw'),
                ('depth/image',     '/camera/depth/image_raw'),
                ('rgb/camera_info', '/camera/camera_info'),
                ('odom',            '/camera/visual_odometry'),  # → EKF
            ]
        ),

        # RTAB-Map SLAM
        Node(
            package='rtabmap_slam',
            executable='rtabmap',
            name='rtabmap',
            output='screen',
            parameters=[rtabmap_config],
            remappings=[
                ('rgb/image',       '/camera/image_raw'),
                ('depth/image',     '/camera/depth/image_raw'),
                ('rgb/camera_info', '/camera/camera_info'),
                ('odom',            '/odometry/filtered'),
            ],
            arguments=['--delete_db_on_start']  # ← bei jedem Start neu beginnen
        ),

    ])