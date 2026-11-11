import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    pkg = get_package_share_directory("robot_localisation")

    # ------------------------------------------------------------------
    # Base de données : on pointe vers la carte EXISTANTE (créée en SLAM)
    # ------------------------------------------------------------------
    save_dir = os.path.expanduser("~/Tuto/src/robot_localisation/maps/small_house")
    save_data = os.path.join(save_dir, "data.db")

    # ------------------------------------------------------------------
    # Launch arguments
    # ------------------------------------------------------------------
    use_viz_arg = DeclareLaunchArgument(
        "use_viz", default_value="true",
        description="Lancer rtabmap_viz (true/false)",
    )
    params_file_arg = DeclareLaunchArgument(
        "params_file",
        default_value=os.path.join(pkg, "config", "rtabmap_localization_params.yaml"),
        description="Fichier YAML des paramètres de LOCALISATION",
    )

    params_file = LaunchConfiguration("params_file")
    remappings = [("scan_cloud", "/scan/points")]

    # ------------------------------------------------------------------
    # Nœud RTAB-Map en mode LOCALISATION
    # ------------------------------------------------------------------
    rtabmap_node = Node(
        package="rtabmap_slam",
        executable="rtabmap",
        name="rtabmap",
        output="screen",
        parameters=[
            params_file,
            {"database_path": save_data},
        ],
        remappings=remappings,
        # ⚠️ PAS de "-d" : on ne veut PAS effacer la carte existante
        arguments=[],
    )

    # ------------------------------------------------------------------
    # rtabmap_viz (optionnel, pour visualiser)
    # ------------------------------------------------------------------
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