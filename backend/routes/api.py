from fastapi import APIRouter
from backend.routes import api_key, video, queries

api_router = APIRouter(prefix="/api")

api_router.include_router(api_key.router, tags=["Google API Key"])
api_router.include_router(queries.router, tags=["Queries"])
api_router.include_router(video.router, tags=["Video"])
