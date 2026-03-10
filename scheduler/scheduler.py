from apscheduler.schedulers.blocking import BlockingScheduler
import redis

r = redis.Redis(host="redis", port=6379, decode_responses=True)
scheduler = BlockingScheduler()

def job():
    print("run job")

print("start schedule")
scheduler.add_job(job, "cron", hour=0, minute=0)
scheduler.start()