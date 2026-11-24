from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

connect_args = {"connect_timeout": 2} if "mysql" in settings.database_url else {}
engine = create_engine(settings.database_url, pool_pre_ping=True, pool_recycle=3600, connect_args=connect_args)
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


def get_db():
    with SessionLocal() as db:
        yield db
