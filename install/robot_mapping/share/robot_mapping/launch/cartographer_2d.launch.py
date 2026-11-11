import os
from launch import LaunchDescription
from ament_index_python.packages import get_package_share_directory
from launch_ros.actions import Node
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration


def generate_launch_description():

    # ------------------------------------------------------------------
    # Launch arguments
    # ------------------------------------------------------------------
    # Répertoire contenant les fichiers .lua de Cartographer
    cartographer_config_dir = LaunchConfiguration("cartographer_config_dir")
    # Nom du fichier .lua (sans chemin)
    configuration_basename = LaunchConfiguration("configuration_basename")
    use_sim_time = LaunchConfiguration("use_sim_time")

    cartographer_config_dir_arg = DeclareLaunchArgument(
        "cartographer_config_dir",
        default_value=os.path.join(
            get_package_share_directory("robot_mapping"),
            "config",
        ),
        description="Full path to the Cartographer config directory (contains .lua files)"
    )

    configuration_basename_arg = DeclareLaunchArgument(
        "configuration_basename",
        default_value="cartographer.lua",
        description="Name of the Lua configuration file (without path)"
    )

    use_sim_time_arg = DeclareLaunchArgument(
        "use_sim_time",
        default_value="true",
        description="Use simulation clock (Isaac Sim)"
    )

    # ------------------------------------------------------------------
    # Lifecycle manager nodes
    # ------------------------------------------------------------------
    # On garde uniquement le map_saver dans le lifecycle manager
    lifecycle_nodes = ["map_saver_server"]

    # ------------------------------------------------------------------
    # Map saver (identique à avant)
    # ------------------------------------------------------------------
    nav2_map_saver = Node(
        package="nav2_map_server",
        executable="map_saver_server",
        name="map_saver_server",
        output="screen",
        parameters=[
            {"save_map_timeout": 5.0},
            {"free_thresh_default": 0.196},
            {"occupied_thresh_default": 0.65},
            {"use_sim_time": use_sim_time},
        ],
    )

    # ------------------------------------------------------------------
    # Cartographer - nœud principal (SLAM)
        # ------------------------------------------------------------------
    cartographer_node = Node(
        package="cartographer_ros",
        executable="cartographer_node",
        name="cartographer_node",
        output="screen",
        parameters=[
            {"use_sim_time": use_sim_time},
            {
                "qos_overrides": {
                    "/scan": {
                        "subscription": {
                            "reliability": "best_effort"
                        }
                    }
                }
            },
        ],
        arguments=[
            "-configuration_directory", cartographer_config_dir,
            "-configuration_basename", configuration_basename,
        ],
        remappings=[("scan", "/scan"),
                        ("odom", "/diff_drive_controller/odom"),],
    )
    # ------------------------------------------------------------------
    # Cartographer - génération de la OccupancyGrid
    # ------------------------------------------------------------------
    cartographer_occupancy_grid_node = Node(
        package="cartographer_ros",
        executable="cartographer_occupancy_grid_node",
        name="cartographer_occupancy_grid_node",
        output="screen",
        parameters=[{"use_sim_time": use_sim_time}],
        arguments=[
            "-resolution", "0.05",
            "-publish_period_sec", "1.0",
        ],
    )

    # ------------------------------------------------------------------
    # Lifecycle manager (uniquement pour map_saver_server)
    # ------------------------------------------------------------------
    nav2_lifecycle_manager = Node(
        package="nav2_lifecycle_manager",
        executable="lifecycle_manager",
        name="lifecycle_manager_slam",
        output="screen",
        parameters=[
            {"node_names": lifecycle_nodes},
            {"autostart": True},
            {"use_sim_time": use_sim_time},
        ],
    )

    # ------------------------------------------------------------------
    # RViz
    # ------------------------------------------------------------------
    rviz = Node(
        package="rviz2",
        executable="rviz2",
        name="rviz2",
        output="screen",
        parameters=[{"use_sim_time": use_sim_time}],
    )

    # ------------------------------------------------------------------
    # Launch description
    # ------------------------------------------------------------------
    return LaunchDescription([
        cartographer_config_dir_arg,
        configuration_basename_arg,
        use_sim_time_arg,
        nav2_map_saver,
        cartographer_node,
        cartographer_occupancy_grid_node,
        nav2_lifecycle_manager,
        rviz,
    ])