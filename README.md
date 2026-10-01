# Differential Drive Mobile Robot — ROS1 Noetic

ROS1 Noetic workspace for a differential-drive mobile robot using an STM32-based motor controller, MPU6050 IMU, RPLIDAR, GMapping, AMCL, and the ROS Navigation Stack.

The project is organized as a standard catkin workspace and is intended for development, mapping, localization, and autonomous navigation experiments on a small indoor mobile robot.

---

## Overview

The system consists of:

- **Orange Pi / Linux SBC** running ROS1 Noetic
- **STM32** for low-level motor control and sensor communication
- **TB6612FNG** dual motor driver
- Two DC motors
- **MPU6050** IMU
- **RPLIDAR**
- Differential-drive chassis

The current ROS architecture is:

```text
                         +------------------+
                         |     RPLIDAR      |
                         +--------+---------+
                                  |
                                /scan
                                  |
                +-----------------+------------------+
                |                                    |
                v                                    v
          GMapping / SLAM                       AMCL / Navigation
                                                     |
                                                  move_base
                                                     |
                                                  /cmd_vel
                                                     |
                                                     v
                                            +------------------+
                                            | motor_controller |
                                            +--------+---------+
                                                     |
                                              UART / STM32
                                                     |
                                      +--------------+--------------+
                                      |                             |
                                      v                             v
                                  Motor A                       Motor B

STM32
  |
  +---- MPU6050 data
             |
             v
       /imu/data_raw
             |
             v
      robot_localization
             |
             v
      odom -> base_link
