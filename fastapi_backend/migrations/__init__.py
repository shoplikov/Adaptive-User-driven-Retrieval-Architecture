"""
Database migration scripts and initialization.
"""

import os
import sys
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.database import Base, init_db
from config import settings


def create_tables():
    """
    Create database tables.
    """
    try:
        init_db()
        logging.info("Database tables created successfully.")
    except Exception as e:
        logging.error(f"Error creating database tables: {e}")
        sys.exit(1)


def drop_tables():
    """
    Drop all database tables.
    """
    try:
        engine = create_engine(settings.DATABASE_URL)
        Base.metadata.drop_all(bind=engine)
        logging.info("Database tables dropped successfully.")
    except Exception as e:
        logging.error(f"Error dropping database tables: {e}")
        sys.exit(1)


if __name__ == "__main__":
    logging.basicConfig(level=settings.log_level_int)
    if len(sys.argv) < 2:
        print("Usage: python -m migrations <create|drop>")
        sys.exit(1)

    command = sys.argv[1].lower()
    if command == "create":
        create_tables()
    elif command == "drop":
        drop_tables()
    else:
        print(f"Unknown command: {command}")
        print("Usage: python -m migrations <create|drop>")
        sys.exit(1)
