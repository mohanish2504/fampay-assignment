from fastapi import APIRouter, Depends, HTTPException
from backend.routes.deps import get_db
from backend.models.api_key import APIKey
from sqlmodel import Session
from loguru import logger
from backend.worker.jobs import fetch_and_store

router = APIRouter(prefix="/api-key")


@router.post(
    "",
    response_model=APIKey,
)
def create_api_key(data: APIKey, db: Session = Depends(get_db)):
    try:
        print(data.model_dump())
        db.add(data)
        db.commit()
        logger.info(f"API Key created: {data.name}")
        return data
    except Exception as e:
        if "UNIQUE constraint failed" in str(e):
            raise HTTPException(status_code=400, detail="API Key already exists")
        logger.exception(f"Error creating API Key: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


# @router.get(
#     "",
# )
# def get_videos(quetry: str):
#     return fetch_and_store(quetry)
