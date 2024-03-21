import os
from sqlmodel import create_engine, SQLModel, Session
from backend.core.config import settings
from backend.models.api_key import *

engine = create_engine(url=settings.DATABASE_URL)
SQLModel.metadata.create_all(engine)
