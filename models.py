from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

# models.py

from pydantic import BaseModel
from sqlalchemy import Column, String, DateTime
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime

# Modelo Pydantic (para a request)
class ScanRequest(BaseModel):
    url: str

# Modelo SQLAlchemy (para o banco de dados)
class Scan(Base):
    __tablename__ = "scans"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    url = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
