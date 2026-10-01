#!/usr/bin/env python3
import math

import rospy
import serial
from sensor_msgs.msg import Imu


def main():
    rospy.init_node('imu_node')

    port = rospy.get_param('~port', '/dev/ttyS2')
    baud = rospy.get_param('~baud', 115200)
    pub = rospy.Publisher('/imu/data_raw', Imu, queue_size=20)

    ser = serial.Serial(port, baud, timeout=0.05)
    ser.reset_input_buffer()
    rospy.loginfo('IMU node connected to %s at %d baud', port, baud)

    while not rospy.is_shutdown():
        try:
            line = ser.readline().decode('ascii', errors='ignore').strip()
            if not line.startswith('$'):
                continue

            values = line[1:].split(',')
            if len(values) != 6:
                continue

            ax, ay, az, gx, gy, gz = [float(x) for x in values]

            msg = Imu()
            msg.header.stamp = rospy.Time.now()
            msg.header.frame_id = 'imu_link'

            acc_scale = 9.80665 / 16384.0
            gyro_scale = math.pi / (180.0 * 131.0)

            msg.linear_acceleration.x = ax * acc_scale
            msg.linear_acceleration.y = ay * acc_scale
            msg.linear_acceleration.z = az * acc_scale
            msg.angular_velocity.x = gx * gyro_scale
            msg.angular_velocity.y = gy * gyro_scale
            msg.angular_velocity.z = gz * gyro_scale

            msg.orientation_covariance[0] = -1.0
            msg.angular_velocity_covariance[0] = 0.0025
            msg.angular_velocity_covariance[4] = 0.0025
            msg.angular_velocity_covariance[8] = 0.0025
            msg.linear_acceleration_covariance[0] = 0.04
            msg.linear_acceleration_covariance[4] = 0.04
            msg.linear_acceleration_covariance[8] = 0.09

            pub.publish(msg)
        except (ValueError, serial.SerialException) as exc:
            rospy.logwarn_throttle(2.0, 'IMU read error: %s', exc)

    ser.close()


if __name__ == '__main__':
    main()
