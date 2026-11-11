import os
from launch import LaunchDescription
from ament_index_python.packages import get_package_share_directory
from launch_ros.actions import Node
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution


def generate_launch_description():

    # ------------------------------------------------------------------
    # Launch arguments
    # ------------------------------------------------------------------
    map_name = LaunchConfiguration("map_name")
    use_sim_time = LaunchConfiguration("use_sim_time")
    amcl_config = LaunchConfiguration("amcl_config")

    map_name_arg = DeclareLaunchArgument(
        "map_name",
        default_value="small_house",
        description="Name of the map folder inside robot_localisation/maps"
    )

    use_sim_time_arg = DeclareLaunchArgument(
        "use_sim_time",
        default_value="true",
        description="Use simulation (Gazebo) clock if true"
    )

    amcl_config_arg = DeclareLaunchArgument(
        "amcl_config",
        default_value=os.path.join(
            get_package_share_directory("robot_localisation"),
            "config",
            "amcl_gazebo.yaml"
        ),
        description="Full path to amcl yaml file to load"
    )

    # ------------------------------------------------------------------
    # Path to map.yaml
    # ------------------------------------------------------------------
    map_path = PathJoinSubstitution([
        get_package_share_directory("robot_localisation"),
        "maps",
        map_name,
        "map.yaml"
    ])

    # ------------------------------------------------------------------
    # Nodes managed by the lifecycle manager
    # ------------------------------------------------------------------
    lifecycle_nodes = ["map_server", "amcl"]

    # ------------------------------------------------------------------
    # Map server
    # ------------------------------------------------------------------
    nav2_map_server = Node(
        package="nav2_map_server",
        executable="map_server",
        name="map_server",
        output="screen",
        parameters=[
            {"yaml_filename": map_path},
            {"use_sim_time": use_sim_time},
        ],
    )

    # ------------------------------------------------------------------
    # AMCL
    # ------------------------------------------------------------------
    nav2_amcl = Node(
        package="nav2_amcl",
        executable="amcl",
        name="amcl",
        output="screen",
        emulate_tty=True,
        parameters=[
            amcl_config,
            {"use_sim_time": use_sim_time},
        ],
    )

    # ------------------------------------------------------------------
    # Lifecycle manager
    # ------------------------------------------------------------------
    nav2_lifecycle_manager = Node(
        package="nav2_lifecycle_manager",
        executable="lifecycle_manager",
        name="lifecycle_manager_localization",
        output="screen",
        parameters=[
            {"node_names": lifecycle_nodes},
            {"autostart": True},
            {"use_sim_time": use_sim_time},
            {"bond_timeout": 0.0},                    # ← empêche le suicide du manager
            {"attempt_respawn_reconnection": True},   # ← retente la connexion si perdue
        ],
    )

        # ------------------------------------------------------------------
    # RViz (avec use_sim_time pour publier les poses au bon timestamp)
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
        map_name_arg,
        use_sim_time_arg,
        amcl_config_arg,
        nav2_map_server,
        nav2_amcl,
        nav2_lifecycle_manager,
        rviz,
    ])