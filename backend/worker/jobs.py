"""
Server should call the YouTube API continuously in background (async) with some interval (say 10 seconds) for fetching the latest videos for a predefined search query and should store the data of videos (specifically these fields - Video title, description, publishing datetime, thumbnails URLs and any other fields you require) in a database with proper indexes.
"""

import datetime
from time import sleep
from celery import Celery
from elasticsearch import Elasticsearch
from loguru import logger
import redis
import requests
from backend.models import Video, APIKey, Queries
from backend.db.redis import redis
from backend.routes.deps import get_elastic_db, get_db
from sqlmodel import select
import redis_lock

from backend.core.config import settings


celery_app = Celery("worker", broker=settings.REDIS_URL)


def create_index(id: str, video: dict, elastic: Elasticsearch):

    logger.info(f"Creating index for video {id}")

    if not elastic.indices.exists(index="video"):
        logger.info("Creating index")
        elastic.indices.create(
            index="video",
            settings={
                "analysis": {
                    "analyzer": {
                        "whitespace": {
                            "type": "custom",
                            "tokenizer": "whitespace",
                        }
                    }
                }
            },
        )

    try:

        elastic.index(index="video", id=id, document=video)
    except Exception as e:
        logger.error(f"Error creating index for video {id} {e}")
        pass


@celery_app.task(name="fetch_and_store", acks_late=True, reject_on_worker_lost=True)
def fetch_and_store(query: str):
    url = "https://www.googleapis.com/youtube/v3/search"
    logger.info(f"Fetching videos for query: {query}")

    # you can uncomment this line, to check if task requeue is working
    # sleep(3)

    # we can also use with Session(engine) as session: but this will make sure to use same function for both sql and elastic
    for session in get_db():
        statement = select(APIKey).where(APIKey.working == True)
        key = session.exec(statement).first()

        if not key:
            logger.error("No API Key available")
            return

        params = {
            "part": "snippet",
            "maxResults": 50,
            "q": query,
            "order": "date",
            "publishedAfter": settings.QUERY_START.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "type": "video",
            "key": key.key,
        }
        response = requests.get(url, params=params)

        result = response.json()
        logger.info(f"Response: {result}")
        if "error" in result:
            logger.error(f"Error fetching videos: {result['error']['message']}")
            if result["error"]["errors"][0]["reason"] == "quotaExceeded":
                statement = select(APIKey).where(APIKey.key == key.key)
                api_key = session.exec(statement).first()
                api_key.working = False
                session.add(api_key)
                session.commit()
                logger.info(f"API Key exshausted/errored: {key.name}")

            # now after marking this key as exshausted we can call the same function again,
            # but since there can be multiple query subjects, its best to wait for 10 seconds and query again and check if any key available.

        else:
            for elastic in get_elastic_db():
                for video in result["items"]:
                    published_at = datetime.datetime.strptime(
                        video["snippet"]["publishedAt"], "%Y-%m-%dT%H:%M:%SZ"
                    )
                    timestamp = published_at.timestamp()
                    video_data = {
                        "title": video["snippet"]["title"],
                        "description": video["snippet"]["description"],
                        "published_at": published_at,
                        # for sorting
                        "thumbnail_urls": video["snippet"]["thumbnails"],
                        "id": video["id"]["videoId"],
                    }

                    # adding in elastic search
                    tags = video["snippet"].get("tags", [])
                    if not tags:
                        tags = video_data["description"].split(" ") + video_data[
                            "title"
                        ].split(" ")
                    video_data["tags"] = tags
                    video = Video(**video_data)
                    create_index(
                        id=video.id,
                        video={
                            "title": video.title,
                            "description": video.description,
                            "published_at": timestamp,  # to sort during query
                            "tags": tags,
                        },
                        elastic=elastic,
                    )

                    # checking if already exists in sql db

                    statement = select(Video).where(Video.id == video_data["id"])
                    existing_video = session.exec(statement).first()

                    if existing_video:
                        logger.info(f"Skipping duplicate video: {video_data['title']}")
                        continue

                    session.add(video)
                    session.commit()

                    logger.info(f"Video added: {video.title}")


@celery_app.task(name="fetch_youtube_videos")
def fetch_youtube_videos():
    """
    This function will be called on all workers, as I haven't implemented scheduler separately.
    To handle this we will be using redis lock, so that only one worker will be able to add job for each query.
    """
    logger.info("Fetching videos")
    lock = redis_lock.RedisLock(redis=redis, lock_key="scheduler_lock", lock_timeout=1)
    if lock.acquire():
        logger.info("Got lock: Fetching videos")
        sleep(2)  # to fail lock request of other workers
        logger.info("Got lock: Adding all video queries")
        for session in get_db():
            statement = select(Queries)
            queries = session.exec(statement).all()
            logger.info(f"Adding {len(queries)} queries")
            for query in queries:
                celery_app.send_task(name="fetch_and_store", args=(query.query,))

        lock.release()
