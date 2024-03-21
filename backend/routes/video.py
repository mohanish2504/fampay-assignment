from fastapi import APIRouter, Depends, HTTPException
from backend.routes.deps import get_elastic_db, get_db
from backend.models.video import Video, VideoFilter
from sqlmodel import Session
from loguru import logger
from sqlmodel import select
from elasticsearch import Elasticsearch

router = APIRouter(prefix="/video")


@router.get(
    "",
    response_model=list[Video],
    description="This will given you all the videos from the database, with the maching query.",
)
def get_videos(
    query: VideoFilter = Depends(VideoFilter),
    elastic: Elasticsearch = Depends(get_elastic_db),
    db: Session = Depends(get_db),
):
    """
    I am not going for pagination here.
    This method will return all the videos from the database.
    """
    try:
        # Search for videos in Elasticsearch
        search_body = {"query": {"match": {"title": query.query}}}
        search_results = elastic.search(index="video", body=search_body)
        matched_ids = [hit["_id"] for hit in search_results["hits"]["hits"]]

        # Retrieve matched videos from the database
        videos = db.exec(select(Video).where(Video.id.in_(matched_ids))).all()

        return videos
    except Exception as e:
        logger.error(f"Error fetching videos {e}")
        raise HTTPException(status_code=500, detail="Error fetching videos")
