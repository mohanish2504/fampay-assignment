from fastapi import APIRouter, Depends, HTTPException
from backend.routes.deps import get_elastic_db, get_db
from backend.models.video import Video, VideoFilter, PaginatedResponse
from sqlmodel import Session
from loguru import logger
from sqlmodel import select
from elasticsearch import Elasticsearch

router = APIRouter(prefix="/video")


@router.get(
    "",
    response_model=PaginatedResponse,
    description="This will given you all the videos from the database, with the maching query.",
)
def get_videos(
    query: VideoFilter = Depends(VideoFilter),
    elastic: Elasticsearch = Depends(get_elastic_db),
    db: Session = Depends(get_db),
):
    """
    This method will return first 10 videos based on the page.
    """
    try:
        # Search for videos in Elasticsearch
        search_body = {
            # This is definitely not the best way to do this
            "query": {"match": {"title": query.query}},
        }
        if not query.query:
            search_body["query"] = {"match_all": {}}

        count = elastic.count(index="video", body=search_body)["count"]
        print(count)

        search_body["from"] = (query.page - 1) * 10
        search_body["size"] = 10
        search_body["sort"] = [{"published_at": {"order": "desc"}}]

        search_results = elastic.search(index="video", body=search_body)
        matched_ids = [hit["_id"] for hit in search_results["hits"]["hits"]]

        print(count)

        stmt = select(Video).where(Video.id.in_(matched_ids))

        # Retrieve matched videos from the database
        videos = db.exec(stmt).all()

        # print(videos)

        return PaginatedResponse(
            count=len(matched_ids),
            items=videos,
            next=query.page + 1 if count > query.page * 10 else None,
            previous=query.page - 1 if query.page > 1 else None,
        )
    except Exception as e:
        logger.error(f"Error fetching videos {e}")
        raise HTTPException(status_code=500, detail="Error fetching videos")
