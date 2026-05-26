from dotenv import load_dotenv
from sqlalchemy import create_engine
from app.core.config import settings

from sqlalchemy.orm import (
    sessionmaker,
    DeclarativeBase
)

from sqlalchemy.pool import QueuePool

import os

load_dotenv()


# =========================================================
# DATABASE URL
# =========================================================

DATABASE_URL = settings.DATABASE_URL


# =========================================================
# SQLALCHEMY ENGINE
# =========================================================

engine = create_engine(
    DATABASE_URL,

    poolclass=QueuePool,

    pool_size=10,

    max_overflow=20,

    pool_pre_ping=True,

    echo=False
)


# =========================================================
# SESSION FACTORY
# =========================================================

SessionLocal = sessionmaker(
    bind=engine,

    autocommit=False,

    autoflush=False,

    expire_on_commit=False
)


# =========================================================
# DECLARATIVE BASE
# =========================================================

class Base(DeclarativeBase):
    pass


# =========================================================
# DATABASE SESSION DEPENDENCY
# =========================================================

def get_db():
    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()