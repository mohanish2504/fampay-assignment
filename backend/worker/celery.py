from datetime import timedelta
from celery import Celery
from backend.core.config import settings
from backend.worker.jobs import celery_app

celery_app.conf.beat_schedule = {
    "fetch_youtube_videos": {
        "task": "fetch_youtube_videos",
        "schedule": timedelta(seconds=10),
    },
}
