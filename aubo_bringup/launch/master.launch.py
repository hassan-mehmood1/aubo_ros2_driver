import os
import atexit
import subprocess
from launch import LaunchDescription
from launch.actions import ExecuteProcess, RegisterEventHandler, TimerAction
from launch.event_handlers import OnProcessExit
from ament_index_python.packages import get_package_prefix

def generate_launch_description():
    pkg_install_dir = get_package_prefix('aubo_bringup')
    scripts_dir = os.path.join(pkg_install_dir, 'lib', 'aubo_bringup')

    start_script_path = os.path.join(scripts_dir, 'aubo_start_mode.py')
    disconnect_script_path = os.path.join(scripts_dir, 'aubo_disconnect.py')

    # Register a clean exit handler for Ctrl+C / shutdown
    def emergency_disconnect():
        print("\n[Launch] Shutdown detected. Executing Aubo disconnect script...")
        try:
            subprocess.run(['python3', disconnect_script_path], check=True)
        except Exception as e:
            print(f"[Launch] Error executing disconnect script: {e}")

    atexit.register(emergency_disconnect)

    # 1. Execute start script first and wait for it to complete (blocks until brakes are released)
    start_robot_process = ExecuteProcess(
        cmd=['python3', start_script_path],
        output='screen'
    )

    # 2. Driver Launch File Action
    driver_launch = ExecuteProcess(
        cmd=[
            'ros2', 'launch', 'aubo_ros2_driver', 'aubo_control.launch.py',
            'aubo_type:=aubo_i5',
            'robot_ip:=192.168.1.188',
            'use_fake_hardware:=false'
        ],
        output='screen'
    )

    # 3. MoveIt Launch File Action
    moveit_launch = ExecuteProcess(
        cmd=[
            'ros2', 'launch', 'aubo_moveit_config', 'aubo_moveit.launch.py',
            'aubo_type:=aubo_i5'
        ],
        output='screen'
    )

    # 4. Chain events: 
    # Once start_script exits, start the driver immediately, 
    # and delay MoveIt by 5 seconds to ensure joint states are actively publishing.
    delayed_ros_launches = RegisterEventHandler(
        event_handler=OnProcessExit(
            target_action=start_robot_process,
            on_exit=[
                driver_launch,
                TimerAction(
                    period=5.0,
                    actions=[moveit_launch]
                )
            ]
        )
    )

    return LaunchDescription([
        start_robot_process,
        delayed_ros_launches
    ])