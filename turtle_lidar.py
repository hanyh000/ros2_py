#json.dumps() 사용: 파이썬 객체(리스트, 딕셔너리 등)를 JSON 문자열로 변환하는 핵심 단계입니다.
#보안: SQL 쿼리에 직접 문자열 포맷팅을 사용하지 말고, 항상 %s와 같은 플레이스홀더를 사용하여 매개변수를 별도로 전달해야 SQL 삽입 공격(SQL injection)을 방지할 수 있습니다.
#데이터 읽기: 나중에 MySQL에서 이 데이터를 다시 파이썬으로 가져올 때는, 보통 문자열 형태로 반환되며 json.loads()를 사용하여 파이썬 리스트/딕셔너리 객체로 다시 변환할 수 있습니다. 
import roslibpy
import pymysql
import time
import numpy as np

import json

DB_CONFIG = dict(
    host="localhost",
    user="root",
    password="as6106",
    database="lidar2",
    charset="utf8"
)

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

    laser = (angle_min, angle_max, angle_increment, range_min, range_max, ranges, intensities)
    
pose_topic = roslibpy.Topic(client, '/scan', 'sensor_msgs/msg/LaserScan')
pose_topic.subscribe(callback)

db = (DB_CONFIG)
conn = pymysql.connect(**db)

while(True) :
    if laser is None:
        print("아직 수신된 Pose 데이터가 없습니다.")
    else :        
        try:
            angle_min, angle_max, angle_increment, range_min, range_max, ranges, intensities = laser

            front = np.r_[ranges[350:360], ranges[0:10]]
            left  = ranges[80:100]
            right = ranges[260:280]

            front_dist = np.mean(front)
            left_dist  = np.mean(left)
            right_dist = np.mean(right)

            safe_dist = 1.3 

            if front_dist < safe_dist and left_dist < safe_dist and right_dist < safe_dist:
                action = "go_back"
            elif front_dist < safe_dist:
                action = "turn_left" if left_dist >= right_dist else "turn_right"
            else:
                action = "go_forward"

            print("front:", round(front_dist, 2))
            print("left :", round(left_dist, 2))
            print("right:", round(right_dist, 2))
            print("action:", action)

            ranges = json.dumps(ranges)

            with conn.cursor() as cur:
                sql = "INSERT INTO `lidardata` (`ranges`, `action`) VALUES (%s, %s)"
                cur.execute(sql, (ranges, action))
            conn.commit()
            print("DB에 저장 완료")
        except Exception as e:
            print("불러오기 실패:", e)
            print("DB 오류:", e)
    time.sleep(0.25)
