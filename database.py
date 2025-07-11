import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import Base  # <-- Importando Base do lugar certo

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost/db")

engine = create_engine(
    DATABASE_URL,
    pool_size=10,
    max_overflow=20,
    pool_timeout=30,
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def setup_database():
    Base.metadata.create_all(bind=engine)
