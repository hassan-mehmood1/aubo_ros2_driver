from pyaubo_sdk import RpcClient

# 1. Connect and login to the controller
client = RpcClient()
client.connect("192.168.1.188", 30004)
client.login("admin", "admin")

# 2. Get robot manager interface
robot_name = client.getRobotNames()[0]
robot_manage = client.getRobotInterface(robot_name).getRobotManage()

# 3. Power off (this safely engages brakes and cuts motor power)
print("Powering off robot motors and engaging brakes...")
robot_manage.poweroff()

# Logout and disconnect
client.logout()
client.disconnect()
print("Robot safely powered down.")
