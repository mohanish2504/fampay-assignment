from typing import Optional
from sqlmodel import SQLModel, Field


class Queries(SQLModel, table=True):
    query: str = Field(nullable=False, primary_key=True)
