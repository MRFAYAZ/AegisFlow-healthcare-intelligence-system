from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):

    # =====================================================
    # PROJECT CONFIG
    # =====================================================

    PROJECT_NAME: str = "AegisFlow"

    DEBUG: bool = True

    API_V1_PREFIX: str = "/api/v1"

    # =====================================================
    # DATABASE CONFIG
    # =====================================================

    DATABASE_URL: str

    # =====================================================
    # JWT CONFIG
    # =====================================================

    JWT_SECRET_KEY: str

    JWT_ALGORITHM: str = "HS256"

    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    class Config:
        env_file = ".env"

        case_sensitive = True


@lru_cache
def get_settings():
    return Settings()


settings = get_settings()