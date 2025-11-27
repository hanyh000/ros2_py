import roslibpy
import time
import numpy as np

HOST = '127.0.0.1' 
PORT = 9090

client = roslibpy.Ros(host=HOST, port=PORT)

print(f"ROS Bridge 서버에 연결 시도 중: ws://{HOST}:{PORT}")
client.run()
laser = None
def callback(message):
    global laser
    angle_min   = message['angle_min']
    angle_max  = message['angle_max']
    angle_increment   = message['angle_increment']
    range_min   = message['range_min']
    range_max = message['range_max']
    ranges = message['ranges']
    intensities   = message['intensities']
    pattern_name = message['pattern_name']

    laser = (angle_min, angle_max, angle_increment, range_min, range_max, ranges, intensities, pattern_name)
    
pose_topic = roslibpy.Topic(client, '/laser_val/laserpub', 'laser_package_msgs/msg/Laser')
pose_topic.subscribe(callback)


while(True) :
    if laser is None:
        print("아직 수신된 Pose 데이터가 없습니다.")
    else :        
        try:
            angle_min, angle_max, angle_increment, range_min, range_max, ranges, intensities, pattern_name = laser

            front = np.r_[ranges[350:360], ranges[0:10]]
            left  = ranges[80:100]
            right = ranges[260:280]

            front_dist = np.mean(front)
            left_dist  = np.mean(left)
            right_dist = np.mean(right)

            safe_dist = 1.3 

            if front_dist < safe_dist:
                action = "turn_left" if left_dist >= right_dist else "turn_right"
            elif front_dist < safe_dist and left_dist <safe_dist and right_dist <safe_dist:
                action = "go_back"
            else:
                action = "go_forward"

            print("front:", round(front_dist, 2))
            print("left :", round(left_dist, 2))
            print("right:", round(right_dist, 2))
            print("action:", action)
            print(pattern_name)
            if action == 'go_forward':
                talker = roslibpy.Topic(client, '/turtle1/cmd_vel', 'geometry_msgs/msg/Twist')
                message = roslibpy.Message({
                    'linear': {'x': 2.0, 'y': 0.0, 'z': 0.0},
                    'angular': {'x': 0.0, 'y': 0.0, 'z': 0.0}
                })
                talker.publish(message)
            elif action == 'turn_left':
                talker = roslibpy.Topic(client, '/turtle1/cmd_vel', 'geometry_msgs/msg/Twist')
                message = roslibpy.Message({
                    'linear': {'x': 0.0, 'y': 0.0, 'z': 0.0},
                    'angular': {'x': 0.0, 'y': 0.0, 'z': 1.55}
                })
                talker.publish(message)
            elif action == 'turn_right':
                talker = roslibpy.Topic(client, '/turtle1/cmd_vel', 'geometry_msgs/msg/Twist')
                message = roslibpy.Message({
                    'linear': {'x': 0.0, 'y': 0.0, 'z': 0.0},
                    'angular': {'x': 0.0, 'y': 0.0, 'z': -1.55}
                })
                talker.publish(message)
            elif action == 'go_back':
                talker = roslibpy.Topic(client, '/turtle1/cmd_vel', 'geometry_msgs/msg/Twist')
                message = roslibpy.Message({
                    'linear': {'x': -2.0, 'y': 0.0, 'z': 0.0},
                    'angular': {'x': 0.0, 'y': 0.0, 'z': 0.0}
                })
                talker.publish(message)
            else :
                talker = roslibpy.Topic(client, '/turtle1/cmd_vel', 'geometry_msgs/msg/Twist')
                message = roslibpy.Message({
                    'linear': {'x': 0.0, 'y': 0.0, 'z': 0.0},
                    'angular': {'x': 0.0, 'y': 0.0, 'z': 0.0}
                })
                talker.publish(message)
        except Exception as e:
            print("불러오기 실패:", e)
    time.sleep(2)
