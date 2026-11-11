# complete_spawn.launch.py with delayed RViz
import os
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, TimerAction
from launch.substitutions import Command
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue
from launch.launch_description_sources import PythonLaunchDescriptionSource
from ament_index_python.packages import get_package_share_directory

def generate_launch_description():
    pkg_path = get_package_share_directory('robot_description')
    urdf_file = os.path.join(pkg_path, 'urdf', 'robot.xacro')
    rviz_config_file= os.path.join(pkg_path , 'rviz' , 'display.rviz')
    # Robot description
    robot_description = ParameterValue(
        Command(['xacro ', urdf_file]),
        value_type=str
    )
    
    # 1. Robot State Publisher
    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        parameters=[{
            'robot_description': robot_description,
            'use_sim_time': True
        }],
        output='screen'
    )

 # Joint State Publisher (GUI pour manipuler les joints)
    joint_state_publisher = Node(
        package='joint_state_publisher_gui',
        executable='joint_state_publisher_gui',
        name='joint_state_publisher_gui',
        output='screen'
    )
    
  

    # 4. RViz2 node with delay (after robot is spawned)
    rviz2 = TimerAction(
        period=5.0,  # Wait 5 seconds before launching RViz
        actions=[
            Node(
                package='rviz2',
                executable='rviz2',
                name='rviz2',
                parameters=[{'use_sim_time': True}],
                arguments=['-d', rviz_config_file],
                output='screen'
            )
        ]
    )
    
    return LaunchDescription([
        robot_state_publisher,
        joint_state_publisher,
        rviz2, 
    ])