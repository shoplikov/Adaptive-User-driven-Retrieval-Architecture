#!/usr/bin/env python3
"""
Intelligent Database Manager for FastAPI Backend

This script automatically discovers SQLAlchemy models and manages database tables.
It provides commands to create, drop, and reset tables with proper relationships.

Usage:
    python db_manager.py create    # Create all tables
    python db_manager.py drop      # Drop all tables
    python db_manager.py reset     # Drop and recreate tables
    python db_manager.py status    # Show table status
"""

import os
import sys
import argparse
import logging
from typing import List, Optional
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine.reflection import Inspector
# Import models from the main database module
import sys
import os

# Add the root directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from fastapi_backend.models.database import Base, engine
from fastapi_backend.config import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

class DatabaseManager:
    """
    Manages database tables with auto-discovery of SQLAlchemy models.
    """

    def __init__(self):
        """Initialize the database manager with connection and inspection."""
        # Create the database URL
        self.engine = engine
        self.inspector = inspect(self.engine)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)

    def get_table_names(self) -> List[str]:
        """Get all table names in the database (fresh inspector each call)."""
        return inspect(self.engine).get_table_names()

    def get_model_table_names(self) -> List[str]:
        """Get table names from SQLAlchemy models."""
        return [table.name for table in Base.metadata.tables.values()]

    def create_tables(self, tables: Optional[List[str]] = None):
        """Create tables for the given models."""
        logger.info("Creating tables...")
        try:
            with self.engine.begin() as conn:  # commits on success
                if not tables:
                    Base.metadata.create_all(bind=conn)
                    logger.info("Successfully created all tables from models")
                else:
                    for table_name in tables:
                        tbl = Base.metadata.tables.get(table_name)
                        if tbl is None:
                            logger.warning(f"Table {table_name} not found in models")
                            continue
                        tbl.create(bind=conn, checkfirst=True)
                        logger.info(f"Created table: {table_name}")
        except SQLAlchemyError as e:
            logger.error(f"Error creating tables: {e}")
            raise

    def drop_tables(self, tables: Optional[List[str]] = None, force: bool = False):
        """Drop tables from the database."""
        if not force:
            confirm = input("WARNING: This will permanently delete tables. Are you sure? (y/N): ").lower()
            if confirm != 'y':
                logger.info("Operation cancelled by user")
                return

        logger.info("Dropping tables...")
        try:
            with self.engine.begin() as conn:  # commits on success
                if not tables:
                    # Drop using metadata (correct FK order)
                    Base.metadata.drop_all(bind=conn)
                else:
                    # Drop specific tables (reverse for FK safety)
                    for table_name in reversed(tables):
                        tbl = Base.metadata.tables.get(table_name)
                        if tbl is None:
                            logger.warning(f"Table {table_name} not found in models")
                            continue
                        tbl.drop(bind=conn, checkfirst=True)
                        logger.info(f"Dropped table: {table_name}")
        except SQLAlchemyError as e:
            logger.error(f"Error dropping tables: {e}")
            raise

    def reset_tables(self, tables: Optional[List[str]] = None):
        """
        Reset tables by dropping and recreating them.
        """
        logger.info("Resetting tables...")

        if not tables:
            # Reset all model tables
            self.drop_tables(force=True)
            self.create_tables()
        else:
            # Reset specific tables
            self.drop_tables(tables, force=True)
            self.create_tables(tables)

    def show_status(self):
        logger.info("Database table status:")
        inspector = inspect(self.engine)  # fresh
        db_tables = set(inspector.get_table_names())
        model_tables = set(self.get_model_table_names())
        extra_tables = db_tables - model_tables
        if extra_tables:
            logger.warning(f"Extra tables in database (not in models): {sorted(extra_tables)}")
        missing_tables = model_tables - db_tables
        if missing_tables:
            logger.warning(f"Tables missing from database: {sorted(missing_tables)}")
        existing_tables = db_tables & model_tables
        if existing_tables:
            logger.info(f"Existing tables: {sorted(existing_tables)}")
        if not extra_tables and not missing_tables:
            logger.info("Database is up to date with models")

    def validate_connection(self):
        """Validate database connection."""
        try:
            with self.engine.connect() as connection:
                result = connection.execute(text("SELECT 1"))
                logger.info("Database connection successful")
                return True
        except SQLAlchemyError as e:
            logger.error(f"Database connection failed: {e}")
            return False

def main():
    """Main entry point for the database manager."""
    parser = argparse.ArgumentParser(description="Intelligent Database Manager")
    parser.add_argument(
        'command',
        choices=['create', 'drop', 'reset', 'status', 'validate'],
        help="Command to execute"
    )
    parser.add_argument(
        '--tables',
        nargs='*',
        help="Specific tables to operate on (optional)"
    )
    parser.add_argument(
        '--force',
        action='store_true',
        help="Force operation without confirmation"
    )

    args = parser.parse_args()

    db_manager = DatabaseManager()

    if args.command == 'create':
        db_manager.create_tables(args.tables)
    elif args.command == 'drop':
        db_manager.drop_tables(args.tables, args.force)
    elif args.command == 'reset':
        db_manager.reset_tables(args.tables)
    elif args.command == 'status':
        db_manager.show_status()
    elif args.command == 'validate':
        db_manager.validate_connection()

if __name__ == "__main__":
    main()