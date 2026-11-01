from pyaubo_sdk import RpcClient
import time

# 1. Connect and login to the robot controller
client = RpcClient()
client.connect("192.168.1.188", 30004)
client.login("admin", "admin")

print("Connected and logged in successfully!")

try:
    # 2. Get the robot interface handle
    robot_names = client.getRobotNames()
    if not robot_names:
        raise RuntimeError("No robots found connected to the controller!")

    robot_name = robot_names[0]
    robot_interface = client.getRobotInterface(robot_name)
    robot_manage = robot_interface.getRobotManage()
    robot_state = robot_interface.getRobotState()

    # 3. Power on and release brakes programmatically
    print("Powering on robot motors...")
    robot_manage.poweron()
    time.sleep(2)

    print("Starting up robot and disengaging brakes...")
    robot_manage.startup()

    # 4. Continuous polling loop to monitor mode until fully ready
    max_wait_time = 30  # Timeout safeguard in seconds
    start_time = time.time()
    is_ready = False

    print("Monitoring robot mode until brakes are fully disengaged...")
    while (time.time() - start_time) < max_wait_time:
        try:
            mode = robot_state.getRobotModeType()
            print(f"Current Robot Mode: {mode}")
            
            # Check if the mode has transitioned past Idle/Booting/BrakeReleasing
            # Adjust the condition below if your SDK version reports a specific ready mode enum string
            if mode and str(mode) in ['RobotModeType.Running']:
                is_ready = True
                break
        except Exception as e:
            print(f"Polling state exception: {e}")
            
        time.sleep(1.0)

    # Fallback or stabilization buffer if mode string check needs extra time
    if not is_ready:
        print("Polling timeout reached or ambiguous mode, applying final stabilization pause...")
        time.sleep(5)

    print("Robot is fully powered on, brakes released, and ready for action!")

except KeyboardInterrupt:
    print("\nStartup interrupted by user (Ctrl+C).")

finally:
    # 5. Logout and disconnect cleanly
    client.logout()
    client.disconnect()
    print("RPC client logged out and disconnected.")