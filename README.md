# Aubo i5 Robot System Startup & Operation Guide

This document outlines the standard operating procedures for booting, running, and safely shutting down the Aubo i5 robot system using the automated ROS 2 bringup workflow.

## 1. Hardware Prerequisites & Safety Checklist

Before powering up or executing any ROS 2 startup scripts, complete the following physical safety and hardware checks:

* [ ] **Pendant Power Switch:** Ensure the power button on the Aubo teach pendant is turned **ON** and the control box is receiving main power.
* [ ] **Emergency Stop (E-Stop):** Confirm that the Emergency Stop button on the teach pendant is disengaged (pulled up / rotated clockwise to release).
* [ ] **Workspace Clearance:** Verify that the robot's physical workspace is clear of human operators, obstacles, and untethered tools.
* [ ] **Network Connection:** Ensure the host PC running ROS 2 is connected to the Aubo controller network (Default IP: `192.168.1.188`).

## 2. Workspace Setup & Repository Structure

Since the `aubo_bringup` package is housed inside your `aubo_ros2_driver` repository, ensure your workspace source layout reflects this structure:

```bash
~/agilex/ros2_ws/src/
└── aubo_ros2_driver/
    └── aubo_bringup/  # Contains master.launch.py, scripts, etc.
```

Prior to launching, build and source your ROS 2 workspace environment:

```bash
# Navigate to the workspace directory
cd ~/agilex/ros2_ws

# Build the packages
colcon build --packages-select aubo_bringup aubo_ros2_driver

# Source the setup script
source install/setup.bash
```

## 3. System Launch (Master Startup Sequence)

To initialize the robot system, run the master launch file:

```bash
ros2 launch aubo_bringup master.launch.py
```

### Automated Launch Workflow:

1. **Hardware Mode Initialization (`aubo_start_mode.py`):**
   * Connects to the Aubo RPC interface at `192.168.1.188:30004`.
   * Programmatically executes `poweron()` and `startup()`.
   * Enters a polling loop monitoring `getRobotModeType()` until the robot reaches `RobotModeType.Running` (approx. 15 seconds).

2. **Driver Initialization (`aubo_control.launch.py`):**
   * Triggered automatically upon completion of the startup mode script.
   * Starts broadcasting joint states and low-level hardware controllers.

3. **MoveIt Motion Planning (`aubo_moveit.launch.py`):**
   * Launched after a 5-second delay following driver startup to ensure `/joint_states` are actively streaming.

## 4. Emergency Stop & Shutdown Procedures

### Normal Shutdown (Graceful Stop)
To terminate the system:
1. Press `Ctrl + C` in the active terminal running `master.launch.py`.
2. The `atexit` hook will automatically execute `aubo_disconnect.py`.
3. Brakes will safely engage, motor power will cut off, and the RPC session will log out cleanly.

### Emergency Shutdown
If an emergency or unexpected motion occurs:
* Immediately press the **Emergency Stop (E-Stop)** button on the Aubo teach pendant.
* Press `Ctrl + C` in the ROS 2 terminal to stop software node execution.

## 5. Troubleshooting & Common Issues

| Issue | Cause | Solution |
| :--- | :--- | :--- |
| **Brake disengagement fails** | E-Stop pressed or Pendant powered off | Ensure teach pendant power is ON and E-Stop switch is released (off). |
| **Connection Timeout** | Incorrect IP or network interface down | Verify physical Ethernet connection and confirm `192.168.1.188` responds to `ping`. |
| **MoveIt Joint State Warnings** | Driver launched concurrently with MoveIt | The master launch handles this via a 5-second delay. Verify `master.launch.py` has the `TimerAction` configured. |