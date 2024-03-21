from typing import Optional
from sqlmodel import SQLModel, Field


class APIKey(SQLModel, table=True):
    key: str = Field(nullable=False, primary_key=True)
    name: Optional[str] = Field(unique=True)
    working: bool = Field(default=True)
