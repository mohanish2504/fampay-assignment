from fastapi import FastAPI
from backend.routes.api import api_router

app = FastAPI(
    title="Fampay Assignment APIs",
    description="Fampay Assignment to fetch videos from youtube and store in db.",
    version="0.1.0",
    openapi_url="/api/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
)


app.include_router(api_router)
