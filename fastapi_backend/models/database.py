"""
Database models and connection management with SQLAlchemy.
"""

import os
from sqlalchemy import create_engine, Column, String, Integer, DateTime, Boolean, Float, JSON, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
from uuid import uuid4
import sys
import os

# Add the root directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from fastapi_backend.config import settings

# Create the database URL
DATABASE_URL = f"postgresql://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}"

# Database base class
Base = declarative_base()

# Database connection
engine = create_engine(DATABASE_URL)
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

class Conversation(Base):
    """
    Database model for conversations.
    """
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    session_id = Column(String(36), unique=True, default=lambda: str(uuid4()))
    user_id = Column(String(255), nullable=True, index=True)
    model = Column(String(255), nullable=False)
    status = Column(String(20), default="active")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    total_tokens = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    extra_data = Column(JSON, nullable=True)
    # Relationship to turns
    turns = relationship("ConversationTurn", back_populates="conversation", order_by="desc(ConversationTurn.created_at)")

class ConversationTurn(Base):
    """
    Database model for conversation turns.
    """
    __tablename__ = "conversation_turns"

    id = Column(Integer, primary_key=True, autoincrement=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"), nullable=False, index=True)
    message_id = Column(String(36), unique=True, default=lambda: str(uuid4()))
    role = Column(String(20), nullable=False, server_default="user")
    content = Column(String, nullable=False)
    message_hash = Column(String(64), index=True, nullable=True)
    tokens = Column(Integer, nullable=True)
    satisfaction_score = Column(String(20), nullable=True)  # 'SAT', 'DSAT', 'Neutral'
    satisfaction_confidence = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    extra_data = Column(JSON, nullable=True)
    # Relationship to conversation
    conversation = relationship("Conversation", back_populates="turns")

# Create tables (if not exists)
def init_db():
    """
    Initialize the database tables.
    """
    Base.metadata.create_all(bind=engine)