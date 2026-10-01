#!/usr/bin/env python3
import math
import threading

import rospy
import serial
from geometry_msgs.msg import Twist
from sensor_msgs.msg import Imu


class BaseController:
    def __init__(self):
        self.port = rospy.get_param('~port', '/dev/ttyS2')
        self.baud = rospy.get_param('~baud', 115200)
        self.wheel_base = rospy.get_param('~wheel_base', 0.1674)
        self.max_wheel_speed = rospy.get_param('~max_wheel_speed', 0.35)
        self.cmd_timeout = rospy.get_param('~cmd_timeout', 0.4)
        self.motor_a_sign = rospy.get_param('~motor_a_sign', 1)
        self.motor_b_sign = rospy.get_param('~motor_b_sign', 1)

        self.lock = threading.Lock()
        self.last_cmd_time = rospy.Time.now()
        self.stopped = True

        self.ser = serial.Serial(self.port, self.baud, timeout=0.02)
        self.ser.reset_input_buffer()

        self.imu_pub = rospy.Publisher('/imu/data_raw', Imu, queue_size=20)
        self.cmd_sub = rospy.Subscriber('/cmd_vel', Twist, self.cmd_vel_callback, queue_size=1)
        self.watchdog = rospy.Timer(rospy.Duration(0.05), self.watchdog_callback)

        rospy.on_shutdown(self.shutdown)
        rospy.loginfo('Base controller connected to %s at %d baud', self.port, self.baud)

    @staticmethod
    def limit(value, low, high):
        return max(low, min(high, value))

    def wheel_to_pwm(self, speed):
        if self.max_wheel_speed <= 0.0:
            return 0
        pwm = int(round(speed / self.max_wheel_speed * 255.0))
        return self.limit(pwm, -255, 255)

    def send_motor(self, motor_a, motor_b):
        command = 'M{},{}\n'.format(motor_a, motor_b)
        with self.lock:
            self.ser.write(command.encode('ascii'))

    def cmd_vel_callback(self, msg):
        v = msg.linear.x
        w = msg.angular.z

        left_speed = v - 0.5 * self.wheel_base * w
        right_speed = v + 0.5 * self.wheel_base * w

        # Current STM32 firmware uses motor A = right, motor B = left.
        motor_a = self.wheel_to_pwm(right_speed) * self.motor_a_sign
        motor_b = self.wheel_to_pwm(left_speed) * self.motor_b_sign

        self.send_motor(motor_a, motor_b)
        self.last_cmd_time = rospy.Time.now()
        self.stopped = (motor_a == 0 and motor_b == 0)

    def watchdog_callback(self, _event):
        age = (rospy.Time.now() - self.last_cmd_time).to_sec()
        if age > self.cmd_timeout and not self.stopped:
            self.send_motor(0, 0)
            self.stopped = True
            rospy.logwarn_throttle(2.0, 'cmd_vel timeout, motors stopped')

    def publish_imu(self, values):
        if len(values) != 6:
            return

        try:
            ax, ay, az, gx, gy, gz = [float(x) for x in values]
        except ValueError:
            return

        msg = Imu()
        msg.header.stamp = rospy.Time.now()
        msg.header.frame_id = 'imu_link'

        scale_acc = 9.80665 / 16384.0
        scale_gyro = math.pi / (180.0 * 131.0)

        msg.linear_acceleration.x = ax * scale_acc
        msg.linear_acceleration.y = ay * scale_acc
        msg.linear_acceleration.z = az * scale_acc

        msg.angular_velocity.x = gx * scale_gyro
        msg.angular_velocity.y = gy * scale_gyro
        msg.angular_velocity.z = gz * scale_gyro

        # MPU6050 packet does not contain an orientation quaternion.
        msg.orientation_covariance[0] = -1.0
        msg.angular_velocity_covariance[0] = 0.0025
        msg.angular_velocity_covariance[4] = 0.0025
        msg.angular_velocity_covariance[8] = 0.0025
        msg.linear_acceleration_covariance[0] = 0.04
        msg.linear_acceleration_covariance[4] = 0.04
        msg.linear_acceleration_covariance[8] = 0.09

        self.imu_pub.publish(msg)

    def read_serial(self):
        while not rospy.is_shutdown():
            try:
                raw = self.ser.readline()
                if not raw:
                    continue

                line = raw.decode('ascii', errors='ignore').strip()
                if line.startswith('$'):
                    self.publish_imu(line[1:].split(','))
            except serial.SerialException as exc:
                rospy.logerr_throttle(2.0, 'Serial error: %s', exc)
                rospy.sleep(0.1)
            except Exception as exc:
                rospy.logwarn_throttle(2.0, 'Serial data error: %s', exc)

    def shutdown(self):
        try:
            self.send_motor(0, 0)
        except Exception:
            pass
        try:
            self.ser.close()
        except Exception:
            pass


def main():
    rospy.init_node('motor_controller')
    controller = BaseController()
    controller.read_serial()


if __name__ == '__main__':
    main()
