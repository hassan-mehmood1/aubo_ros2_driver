# aubo_ros2_driver

Robot ROS2 drive

## View the aubo robot model in rviz (using aaubo_i5 as an example)

```bash
ros2 launch aubo_description aubo_viewer.launch.py
```

## Priority for URDF Calibration

It is recommended to generate a calibration version of URDF based on the calibration compensation returned by the robot's current controller, and then perform real-machine drive, MoveIt planning, and trajectory verification.

If you use the uncalibrated default URDF directly, there may be the following risks:

- The planning model is inconsistent with the real robot kinematic parameters, and the end position is biased.
- The attitude and real feedback in RViz and MoveIt are not exactly the same, affecting the problem positioning.
- TCP validation, trajectory replication, and offline point-to-point matching depend on the precision of the model, and the results may be unreliable.

Recommended Methods:

```bash
cd /root/Desktop/aubo_ros2_ws
python3 src/aubo_description/scripts/calibrate_urdf_dh.py \
  --robot-model aubo_i5 \
  --robot-ip 192.168.1.188
colcon build --packages-select aubo_description
```

Description:

- Generate results written by default  `src/aubo_description/urdf/<robot_model>_calibrated.urdf`.
- `--robot-ip` It needs to be clearly introduced.
- Before running, make sure that the current Python environment can be imported  `numpy` and `pyaubo_sdk`。
- It needs to be re-compiled separately after generation.  `aubo_description` The bag.

## Drive the real robotic arm aubo_i5 (modify the robot corresponding) `robot_ip`、`aubo_type`）

```bash
source install/setup.bash
ros2 launch aubo_ros2_driver aubo_control.launch.py aubo_type:=aubo_i5 robot_ip:=192.168.1.188 \
  use_fake_hardware:=false
ros2 launch aubo_moveit_config aubo_moveit.launch.py aubo_type:=aubo_i5
```

## Drive the real robotic arm aubo_i5 single-point trajectory execution demo (modify robot correspondence) `robot_ip`、`aubo_type`）

```bash
source install/setup.bash
ros2 launch aubo_ros2_driver aubo_control.launch.py aubo_type:=aubo_i5 robot_ip:=192.168.1.188 \
  use_fake_hardware:=false
ros2 launch ros_joints_plan joints_plan.launch.py aubo_type:=aubo_i5
```

## Service node drives the real robot arm (modifies the robot corresponding) `robot_ip`）

```bash
source install/setup.bash
ros2 launch aubo_ros2_driver aubo_client.launch.py robot_ip:=127.0.0.1 log_level:=info
```

## Independent Topic command node

The node controls the arm directly through the AUBO SDK and does not use the ros2_control hardware plug-in. Do not start other drives that control the same robotic arm at the same time.

```bash
source install/setup.bash
ros2 launch aubo_ros2_driver aubo_command.launch.py robot_ip:=192.168.1.188
```
Command the topic:

- `/aubo/power_command` (`aubo_msgs/msg/AuboPowerCommand`)：`power_on=true` powering and starting,`false` Electricity.
- `/aubo/joint_move` (`aubo_msgs/msg/AuboJointMove`)： Six-axis joint target, angle using rad/s, speed using rad/s, acceleration using rad/s^2.
- `/aubo/linear_move` (`aubo_msgs/msg/AuboLinearMove`)：The goal  `PoseStamped`，Must be used with configuration.  `base_frame`（The acquiescence `base_link`）；Position unit meter, velocity/acceleration unit m/s, m/s2.

### Powered up and down

The power-on command will ask the robot arm to be powered on and started (spine brakes) and wait to enter Running mode:

```bash
ros2 topic pub --once /aubo/power_command aubo_msgs/msg/AuboPowerCommand \
"{command_id: 'power-on-001', power_on: true}"
```

Order by electricity:

```bash
ros2 topic pub --once /aubo/power_command aubo_msgs/msg/AuboPowerCommand \
"{command_id: 'power-off-001', power_on: false}"
```

### 关节运动

先确认机械臂处于可运动状态，并根据机器人型号、当前姿态和工作空间设置安全的六轴目标。以下仅为消息格式示例；位置单位为弧度：

```bash
ros2 topic pub --once /aubo/joint_move aubo_msgs/msg/AuboJointMove \
"{command_id: 'joint-001', positions: [0.0, -0.2, 0.3, 0.0, 0.2, 0.0], max_velocity: 0.2, max_acceleration: 0.4}"
```

### 直线运动

目标位姿以 `base_frame` 为参考坐标系，默认是 `base_link`。位置单位为米，方向使用四元数；速度单位为 m/s，加速度单位为 m/s^2，混合半径单位为米。下面的位姿只展示消息格式，使用前要确认目标在机械臂可达且无碰撞的工作空间内：

```bash
ros2 topic pub --once /aubo/linear_move aubo_msgs/msg/AuboLinearMove \
"{command_id: 'linear-001', target: {header: {frame_id: 'base_link'}, pose: {position: {x: 0.30, y: 0.0, z: 0.30}, orientation: {x: 0.0, y: 0.0, z: 0.0, w: 1.0}}}, speed: 0.05, acceleration: 0.1, blend_radius: 0.0}"
```

### 查看执行结果

在另一个终端订阅状态 Topic：

```bash
ros2 topic echo /aubo/command_status
```

每条命令的 `command_id` 必须非空，建议每次请求使用唯一值。状态包括 `accepted`、`running`、`succeeded`、`failed` 和 `rejected`。节点一次只接收一条命令执行；正在执行时发布的新命令会以 `rejected` 状态返回。若收到 `failed` 或 `rejected`，请检查状态消息的 `message` 字段及节点日志。

该节点直接通过 AUBO SDK 控制机器人。不要同时启动其他会控制同一机械臂的驱动。上电/下电 Topic 不是急停接口；急停必须使用机器人控制柜或安全系统提供的硬件安全功能。

## 调用示例

```bash
source install/setup.bash
ros2 service call /jsonrpc_service aubo_msgs/srv/JsonRpc \
"{cls: 'RobotState', func: 'getTcpPose', params: '[]'}"
```

## 响应示例

```bash
requester: making request: aubo_msgs.srv.JsonRpc_Request(cls='RobotState', func='getTcpPose', params='[]')

response:
aubo_msgs.srv.JsonRpc_Response(result='[0.0, 0.0, 0.0, 0.0, 0.0, 0.0]', error='None')
```

## 异常响应示例（输入错误类 `RobotStat`）

```bash
requester: making request: aubo_msgs.srv.JsonRpc_Request(cls='RobotStat', func='getTcpPose', params='[]')

response:
aubo_msgs.srv.JsonRpc_Response(result='None', error='{"code": -32601, "message": "method not found: rob1.RobotStat.getTcpPose"}')
```

## aubo_sdk 接口参考文档

[aubo_sdk developer](https://docs.aubo-robotics.cn/arcs_api/index.html)
