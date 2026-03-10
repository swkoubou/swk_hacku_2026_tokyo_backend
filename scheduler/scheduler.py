from apscheduler.schedulers.blocking import BlockingScheduler

scheduler = BlockingScheduler()

def job():
    print("run job")
    
print("start schedule")
scheduler.add_job(job, "cron", hour=0, minute=0)
scheduler.start()