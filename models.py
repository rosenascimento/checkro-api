from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Scan(Base):
    __tablename__ = "scans"
    id = Column(String, primary_key=True)
    url = Column(String)
    status = Column(String)
    created_at = Column(Integer)

class Issue(Base):
    __tablename__ = "issues"
    id = Column(Integer, primary_key=True)
    scan_id = Column(String, ForeignKey("scans.id"))
    page_url = Column(String)
    rule_code = Column(String)
    description = Column(Text)
    term_detected = Column(Text, nullable=True)
    suggestion = Column(Text)
