from datetime import datetime
from typing import Optional
from sqlmodel import Field, SQLModel, JSON, Column, DateTime
from pydantic import BaseModel


class Video(SQLModel, table=True):
    title: str = Field(nullable=False)
    description: str = Field(nullable=False)
    published_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), nullable=False)
    )
    thumbnail_urls: dict = Field(sa_column=Column(JSON, nullable=False))
    id: str = Field(nullable=False, primary_key=True)


class VideoFilter(BaseModel):
    query: Optional[str] = None
