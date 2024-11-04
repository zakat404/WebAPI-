from pydantic_settings import BaseSettings
from pydantic import ConfigDict

class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+asyncpg://user:password@db:5432/image_db"
    SECRET_KEY: str = "your-secret-key"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    BROKER_URL: str = "amqp://guest:guest@broker:5672/"
    REDIS_URL: str = "redis://cache:6379/0"
    model_config = ConfigDict(env_file=".env")

settings = Settings()
