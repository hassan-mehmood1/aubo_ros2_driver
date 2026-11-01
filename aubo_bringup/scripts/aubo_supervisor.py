from pyaubo_sdk import RpcClient
import time
import sys

def main():
    client = RpcClient()
    try:
        print("Connecting to Aubo controller...")
        client.connect("192.168.1.188", 30004)
        client.login("admin", "admin")
        print("Connected and logged in successfully!")

        robot_names = client.getRobotNames()
        if not robot_names:
            raise RuntimeError("No robots found connected to the controller!")

        robot_name = robot_names[0]
        robot_interface = client.getRobotInterface(robot_name)
        robot_manage = robot_interface.getRobotManage()
        robot_state = robot_interface.getRobotState()

        print("Powering on robot motors...")
        robot_manage.poweron()
        time.sleep(2)

        print("Starting up robot and disengaging brakes...")
        robot_manage.startup()

        # Polling loop until Running state is reached
        max_wait_time = 30
        start_time = time.time()
        is_ready = False

        print("Monitoring robot mode until brakes are fully disengaged...")
        while (time.time() - start_time) < max_wait_time:
            try:
                mode = robot_state.getRobotModeType()
                print(f"Current Robot Mode: {mode}")
                if mode and str(mode) in ['RobotModeType.Running']:
                    is_ready = True
                    break
            except Exception:
                pass
            time.sleep(1.0)

        if not is_ready:
            print("Polling timeout reached, applying final stabilization pause...")
            time.sleep(5)

        print("Robot is fully powered on and ready! Supervisor active (Press Ctrl+C to shutdown)...")

        # KEEP ALIVE: Stay running in the background so we can catch Ctrl+C anytime
        while True:
            time.sleep(1.0)

    except KeyboardInterrupt:
        print("\nCtrl+C detected! Safely powering off robot motors and engaging brakes...")
        try:
            robot_manage.poweroff()
            client.logout()
            client.disconnect()
            print("Robot safely powered down and disconnected.")
        except Exception as e:
            print(f"Error during shutdown: {e}")
        sys.exit(0)

    except Exception as e:
        print(f"Error in supervisor: {e}")
        try:
            client.logout()
            client.disconnect()
        except:
            pass
        sys.exit(1)

if __name__ == '__main__':
    main()