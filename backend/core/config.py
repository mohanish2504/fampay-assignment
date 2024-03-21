from datetime import datetime
from typing import Any, Dict, Optional
from pydantic import RedisDsn, validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_FILE_PATH: str = "database.db"

    ELASTICSEARCH_URL: str = "http://localhost:9200"

    INTERVAL_SECONDS: int = 60
    QUERY_START: datetime

    REDIS_PASSWORD: str = "abcdef"

    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_USER: str = ""

    REDIS_URL: Optional[str] = None

    @validator("REDIS_URL", pre=True)
    def assemble_redis_db_connection(
        cls, v: Optional[str], values: Dict[str, Any]
    ) -> Any:

        if isinstance(v, str):
            return v
        url = RedisDsn.build(
            scheme="redis",
            username=values.get("REDIS_USER"),
            password=values.get("REDIS_PASSWORD"),
            host=values.get("REDIS_HOST"),
            port=values.get("REDIS_PORT"),
        )

        return str(url)

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
