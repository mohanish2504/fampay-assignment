from elasticsearch import Elasticsearch
from backend.db.sql import engine
from sqlmodel import Session
from backend.core.config import settings
from redis import Redis

def get_db():
    db = Session(engine, expire_on_commit=False)
    try:
        yield db
    finally:
        db.close()


def get_elastic_db():
    elastic = Elasticsearch(settings.ELASTICSEARCH_URL)
    try:
        result = elastic.ping()
        if not result:
            raise ValueError("Failed to connect to Elasticsearch")
        yield elastic
    finally:
        elastic.close()

