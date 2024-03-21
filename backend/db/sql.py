import os
from sqlmodel import create_engine, SQLModel, Session
from backend.core.config import settings
from backend.models.api_key import *
from loguru import logger

engine = create_engine(url="sqlite:///./storage/" + settings.DATABASE_FILE_PATH)
SQLModel.metadata.create_all(engine)
