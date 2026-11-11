import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    pkg = get_package_share_directory("robot_mapping")

    save_dir = os.path.expanduser("~/Tuto/src/robot_mapping/maps/small_house")
    os.makedirs(save_dir, exist_ok=True)
    save_data = os.path.join(save_dir, "data.db")

    
    use_viz_arg = DeclareLaunchArgument(
        "use_viz", default_value="true",
        description="Lancer rtabmap_viz (true/false)",
    )
    params_file_arg = DeclareLaunchArgument(
        "params_file",
        default_value=os.path.join(pkg, "config", "rtabmap_params.yaml"),
        description="Fichier YAML des paramètres RTAB-Map",
    )

    params_file = LaunchConfiguration("params_file")
    remappings = [("scan_cloud", "/scan/points")]

    rtabmap_node = Node(
        package="rtabmap_slam",
        executable="rtabmap",
        name="rtabmap",
        output="screen",
        parameters=[params_file ,{"database_path": save_data},],  
        #Le -d (delete) fait exactement ce que tu veux éviter 
        #Si tu relances, ta carte précédente sera détruite   a nouvelle session repart de zéro   Pour conserver la carte entre sessions, retire -d
        remappings=remappings,
        arguments=["-d"],  # supprime la base à chaque démarrage
    )

    rtabmap_viz_node = Node(
        package="rtabmap_viz",
        executable="rtabmap_viz",
        name="rtabmap_viz",
        output="screen",
        condition=IfCondition(LaunchConfiguration("use_viz")),
        parameters=[params_file],
        remappings=remappings,
    )

    return LaunchDescription([
        use_viz_arg,
        params_file_arg,
        rtabmap_node,
        rtabmap_viz_node,
    ])