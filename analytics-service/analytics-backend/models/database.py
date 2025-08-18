"""Database models and connection management with SQLAlchemy."""
import os
import sys
from sqlalchemy import (
    create_engine,
    Column,
    String,
    Integer,
    DateTime,
    Boolean,
    Float,
    JSON,
    ForeignKey,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from typing import Optional

# Add the root directory to the Python path
sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
)

# Database base class
Base = declarative_base()

# Database connection
DATABASE_URL = os.getenv(
    "ANALYTICS_DATABASE_URL", "postgresql://postgres:master@localhost:5432/analytics"
)


# SQLAlchemy models
class Conversation(Base):
    """Conversation model representing chatbot interactions"""

    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True)
    satisfaction = Column(String)  # 'positive', 'neutral', 'negative'
    input_tokens = Column(Integer, default=0)
    output_tokens = Column(Integer, default=0)
    status = Column(String)  # 'active', 'inactive', 'ended'
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)


engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
    bind=engine,
)


def get_db():
    """
    Dependency that provides a SQLAlchemy session.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Create tables (if not exists)
def init_db():
    """Initialize the database tables."""
    Base.metadata.create_all(bind=engine)
