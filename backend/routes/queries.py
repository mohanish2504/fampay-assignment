from fastapi import APIRouter, Depends, HTTPException
from backend.models.queries import Queries
from backend.routes.deps import get_db
from sqlmodel import Session
from loguru import logger

router = APIRouter(prefix="/queries")


@router.post(
    "",
    response_model=Queries,
    description="You can add queries here this will be used to fetch videos from youtube.",
)
def create_query(data: Queries, db: Session = Depends(get_db)):
    try:
        db.add(data)
        db.commit()
        logger.info(f"Query created: {data.query}")
        return data
    except Exception as e:
        if "UNIQUE constraint failed" in str(e):
            raise HTTPException(status_code=400, detail="Query already exists")
        logger.exception(f"Error creating Query Key: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
