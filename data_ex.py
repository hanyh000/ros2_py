import pymysql
import json
import pandas as pd

df = pd.DataFrame()

conn = pymysql.connect(
    host='localhost',
    user='root',
    password='1234',
    database='rosdb',
    charset='utf8'
)

cursor = conn.cursor()

cursor.execute("SELECT ranges, action FROM lidardata")

rows = cursor.fetchall()

for r in rows:
    ranges = json.loads(r[0])
    action = r[1]
    
    row = pd.DataFrame([ {i: v for i, v in enumerate(ranges)} ])
    row['action'] = action
    df = pd.concat([df, row], ignore_index=True)

print(df)
df.to_csv('output.csv', index=False)
cursor.close()
conn.close()