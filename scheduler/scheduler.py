from apscheduler.schedulers.blocking import BlockingScheduler
import redis
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import date
import json

connection = psycopg2.connect("host=postgres dbname=calendar user=app password=app")
cursor = connection.cursor(cursor_factory=RealDictCursor)

r = redis.Redis(host="redis", port=6379, decode_responses=True)

scheduler = BlockingScheduler()

def job():
    with open("log.txt", "a", encoding="utf-8") as f:
        f.write(f"start scheduler {date.today()}\n")
    try: 
        cursor.execute(
            """
            SELECT
                task_id,
                user_uuid,
                TO_CHAR(start_date, 'YYYY-MM-DD') as start_date,
                TO_CHAR(start_time, 'HH24:MI:SS') as start_time,
                TO_CHAR(end_date, 'YYYY-MM-DD') as end_date,
                event_name
            FROM events
            WHERE start_date = %s
            """,
            (date.today(),)
        )
        query_result = cursor.fetchall()
    except Exception as e:
        print(e)
    count=0
    pipe = r.pipeline()
    for event in query_result:
        data={
            "user_uuid": event["user_uuid"],
            "task_uuid": event["task_id"],
            "start_date": event["start_date"],
            "start_time": event["start_time"],
            "end_date": event["end_date"],
            "event_name": event["event_name"],
            "done":False
        }
        pipe.set(f"event:{event['user_uuid']}:{event['task_id']}", json.dumps(data), ex=86400)
        count+=1
    pipe.execute()
    with open("log.txt", "a", encoding="utf-8") as f:
        f.write(f"finish scheduler {date.today()} count:{count}\n")

print("start schedule")
scheduler.add_job(job, "cron", hour=0, minute=0)
#scheduler.add_job(job, "interval", seconds=10) #debug
scheduler.start()