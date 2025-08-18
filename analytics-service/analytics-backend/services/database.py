"""Database service for analytics queries"""
from typing import List, Dict, Any
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
import logging

logger = logging.getLogger(__name__)


class DatabaseService:
    """Service class for handling database operations for analytics"""

    def __init__(self, db_url: str):
        """Initialize database service with connection URL"""
        logger.info(f"Initializing database service with URL: {db_url}")
        self.engine = create_engine(db_url)
        logger.info(f"Created database engine: {self.engine}")
        self.Session = sessionmaker(bind=self.engine)
        logger.info("Database service initialized successfully")

    def execute_query(
        self, query: str, params: Dict[str, Any] = None
    ) -> List[Dict[str, Any]]:
        """
        Execute a raw SQL query and return results as a list of dictionaries

        Args:
            query: SQL query string
            params: Optional parameters for the query

        Returns:
            List of dictionaries representing query results

        Raises:
            SQLAlchemyError: If database operation fails
        """
        session = self.Session()
        try:
            result = session.execute(text(query), params or {})
            logger.info(f"Query executed successfully: {query}")

            # Convert SQLAlchemy result rows to dictionaries properly
            rows = []
            for row in result:
                try:
                    # Try the _asdict() method first (works with newer SQLAlchemy)
                    if hasattr(row, "_asdict"):
                        row_dict = row._asdict()
                        logger.debug(f"Converted row using _asdict(): {row_dict}")
                    # Try accessing as mapping (works with SQLAlchemy result rows)
                    elif hasattr(row, "_mapping"):
                        row_dict = dict(row._mapping)
                        logger.debug(f"Converted row using _mapping: {row_dict}")
                    # Fallback to manual key-value extraction
                    else:
                        row_dict = {key: getattr(row, key) for key in row.keys()}
                        logger.debug(
                            f"Converted row using manual extraction: {row_dict}"
                        )
                    rows.append(row_dict)
                except Exception as conversion_error:
                    logger.error(f"Error converting row to dict: {conversion_error}")
                    logger.error(f"Row object type: {type(row)}")
                    logger.error(f"Row object: {row}")
                    logger.error(f"Row attributes: {dir(row)}")
                    raise

            logger.info(f"Successfully converted {len(rows)} rows to dictionaries")
            return rows
        except SQLAlchemyError as e:
            logger.error(f"Database error executing query: {e}")
            raise
        finally:
            session.close()

    def get_total_conversations(self) -> int:
        """Get total number of conversations"""
        query = "SELECT COUNT(*) as total FROM conversations"
        results = self.execute_query(query)
        return results[0]["total"] if results else 0

    def get_satisfaction_stats(self) -> Dict[str, int]:
        """Get satisfaction statistics"""
        query = """
        SELECT
            satisfaction,
            COUNT(*) as count
        FROM conversations
        GROUP BY satisfaction
        """
        results = self.execute_query(query)
        stats = {row["satisfaction"]: row["count"] for row in results}
        return stats

    def get_token_usage(self) -> Dict[str, int]:
        """Get token usage statistics"""
        query = """
        SELECT
            SUM(input_tokens) as input_tokens,
            SUM(output_tokens) as output_tokens
        FROM conversations
        """
        results = self.execute_query(query)
        if not results:
            return {"input_tokens": 0, "output_tokens": 0}
        return results[0]

    def get_status_breakdown(self) -> Dict[str, int]:
        """Get conversation status breakdown"""
        query = """
        SELECT
            status,
            COUNT(*) as count
        FROM conversations
        GROUP BY status
        """
        results = self.execute_query(query)
        breakdown = {row["status"]: row["count"] for row in results}
        return breakdown
