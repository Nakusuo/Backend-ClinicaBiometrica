from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings


FreePBXSessionLocal = None

if settings.freepbx_database_url:
    freepbx_engine = create_engine(
        settings.freepbx_database_url,
        pool_pre_ping=True,
    )
    FreePBXSessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=freepbx_engine,
    )


def get_freepbx_db():
    if FreePBXSessionLocal is None:
        return None

    db = FreePBXSessionLocal()
    try:
        return db
    finally:
        pass
