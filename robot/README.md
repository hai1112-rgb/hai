# Mobile robot ROS workspace

ROS Noetic workspace for the differential-drive robot.

## Main nodes

- RPLidar publishes `/scan`.
- `motor_controller` opens the STM32 UART, subscribes to `/cmd_vel` and publishes `/imu/data_raw` from the MPU6050 packet.
- `robot_localization` publishes the `odom -> base_link` transform.
- `gmapping.launch` is used to create a map.
- `navigation.launch` starts AMCL and `move_base` with a saved map.

The STM32 serial format currently used by the ROS node is:

```text
M<pwm_a>,<pwm_b>\n
$ax,ay,az,gx,gy,gz\n
```

`ax..gz` are raw MPU6050 values. Gyro values are converted to rad/s before publishing the ROS IMU message.

## Build

```bash
cd ~/robot/catkin_ws
catkin_make
source devel/setup.bash
```

## Run the robot

```bash
roslaunch robot_bringup robot.launch
```

If the motor direction is reversed, change `motor_a_sign` or `motor_b_sign` in `robot.launch` from `1` to `-1`.

## Mapping

```bash
roslaunch robot_bringup gmapping.launch
```

After mapping, save it to `robot_bringup/maps`:

```bash
rosrun map_server map_saver -f ~/robot/catkin_ws/src/robot_bringup/maps/map
```

## Navigation

```bash
roslaunch robot_bringup navigation.launch
```

Wheel encoder odometry is not in this version yet. For stable navigation, encoder feedback from the STM32 should be added and fused with the IMU in `robot_localization`.
