# 노드 부분
#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan
import random 
import math

ANGLE_MIN_DEG = 0
ANGLE_MAX_DEG = 359
ANGLE_INCREMENT_DEG = 1
NUM_POINTS = 360
RANGE_MIN = 0.12
RANGE_MAX = 3.5
AVAILABLE_PATTERNS = [
    "front_wall",
    "left_wall",
    "right_wall"
]
class MyTopicHandler(Node):
    def __init__(self):
        super().__init__('lidar_node')

        self.publisher = self.create_publisher(
            LaserScan,
            '/lidar_data_mock',
            10
        )

        self.timer = self.create_timer(2.0, self.timer_callback)   # 0.5Hz초마다 실행

    def create_empty_scan(self):
        ranges = [RANGE_MAX for _ in range(NUM_POINTS)]
        intensities = [100.0 for _ in range(NUM_POINTS)]
        scan = {
            "angle_min": math.radians(ANGLE_MIN_DEG),
            "angle_max": math.radians(ANGLE_MAX_DEG),
            "angle_increment": math.radians(ANGLE_INCREMENT_DEG),
            "range_min": RANGE_MIN,
            "range_max": RANGE_MAX,
            "ranges": ranges,
            "intensities": intensities
        }
        return scan

    def make_the_wall(self, ranges, center_deg, width_deg):
        half_width = width_deg // 2
        for offset in range(-half_width, half_width + 1):
            idx = (center_deg + offset) % NUM_POINTS
            ranges[idx] = 0.4

    def pattern_front_wall(self, scan):
        self.make_the_wall(scan["ranges"], center_deg=0, width_deg=40)

    def pattern_left_wall(self, scan):
        self.make_the_wall(scan["ranges"], center_deg=90, width_deg=30)

    def pattern_right_wall(self, scan):
        self.make_the_wall(scan["ranges"], center_deg=270, width_deg=30)

    def generate_single_scan(self, pattern_name):
        scan = self.create_empty_scan()
        if pattern_name == "front_wall":
            self.pattern_front_wall(scan)
        elif pattern_name == "left_wall":
            self.pattern_left_wall(scan)
        elif pattern_name == "right_wall":
            self.pattern_right_wall(scan)
        return scan

    def timer_callback(self):

        pattern_name = random.choice(AVAILABLE_PATTERNS)
        scan = self.generate_single_scan(pattern_name)

        my_msg = LaserScan()
        my_msg.angle_min = scan['angle_min']
        my_msg.angle_max = scan['angle_max']
        my_msg.angle_increment = scan['angle_increment']
        my_msg.range_min = scan['range_min']
        my_msg.range_max = scan['range_max']
        my_msg.ranges = scan['ranges']
        my_msg.intensities = scan['intensities']

        self.publisher.publish(my_msg)


def main(args=None):
    rclpy.init(args=args)
    node = MyTopicHandler()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()

# 원격 제어 부분
import roslibpy
import numpy as np 

client = roslibpy.Ros(host='localhost', port=9090)
client.run()
print('Connected to ROS!')


cmd_vel_pub = roslibpy.Topic(
            client,
            '/turtle1/cmd_vel',
            'geometry_msgs/msg/Twist'
        )
listener = roslibpy.Topic(client,
                            '/lidar_data_mock',
                            'sensor_msgs/msg/LaserScan')  

def callback(message):
    ranges = np.array(message["ranges"])

    front = np.r_[ranges[350:360], ranges[0:10]]
    left  = ranges[80:100]
    right = ranges[260:280]

    front_dist = np.mean(front)
    left_dist  = np.mean(left)
    right_dist = np.mean(right)

    safe_dist = 0.5

    if front_dist < safe_dist:
        if left_dist > right_dist :
            action = "turn_left"
            cmd_vel_pub.publish({
                'linear': {'x': 0.0, 'y': 0.0, 'z': 0.0},
                'angular': {'x': 0.0, 'y': 0.0, 'z': 1.0}
            })
        else :
            action = "turn_right"
            cmd_vel_pub.publish({
                'linear': {'x': 0.0, 'y': 0.0, 'z': 0.0},
                'angular': {'x': 0.0, 'y': 0.0, 'z': -1.0}
            })
    else:
        action = "go_forward"
        cmd_vel_pub.publish({
            'linear': {'x': 0.5, 'y': 0.0, 'z': 0.0},
            'angular': {'x': 0.0, 'y': 0.0, 'z': 0.0}
        })

    print("front:", round(front_dist, 2))
    print("left :", round(left_dist, 2))
    print("right:", round(right_dist, 2))
    print("action:", action)

try:
    listener.subscribe(callback)

    while client.is_connected:
        pass
except KeyboardInterrupt:
    pass
finally:
    listener.unsubscribe()
    client.terminate()
    print('Disconnected.')