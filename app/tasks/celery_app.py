from celery import Celery
from celery.schedules import crontab
from app.config import settings

celery_worker = Celery(
    "tasks",
    broker=f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/0",
    include=[
        "app.tasks.tasks",
        "app.tasks.scheduled",
    ]
)


celery_worker.conf.beat_schedule = {
    "luboe-nazvanie": {
        "task": "periodic_task",
        #"schedule": 5,  # секунды
        "schedule": crontab(minute="00", hour="00"),
    }
}