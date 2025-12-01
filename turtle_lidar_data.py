import pymysql

import json
import csv

DB_CONFIG = dict(
    host="localhost",
    user="root",
    password="as6106",
    database="lidar2",
    charset="utf8"
)


db = (DB_CONFIG)
conn = pymysql.connect(**db)

with conn.cursor() as cur:
    cur = conn.cursor(pymysql.cursors.SSCursor)
    cur.execute("SELECT ranges FROM lidardata")
    ranges = cur.fetchall()

    cur.execute("SELECT action FROM lidardata")
    action = cur.fetchall()
ranges = [json.loads(r[0]) for r in ranges]
action = [a[0] for a in action]

fieldnames = [str(i) for i in range(360)] + ['action']
with open('lidar_test2.csv', 'w', newline='', encoding='utf-8') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)  # 첫 번째 인자: 파일
    writer.writeheader()

    for range_row, action_value in zip(ranges, action):
        row = {str(i): range_row[i] for i in range(360)}  # 0~359 값 저장
        row['action'] = action_value
        writer.writerow(row)

print("csv 파일이 생성되었습니다.")