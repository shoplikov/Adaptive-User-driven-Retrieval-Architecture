"""Analytics service for AURA conversation metrics"""
import logging
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, text
from sqlalchemy.exc import SQLAlchemyError

from models.schemas import (
    MetricsOverview, SatisfactionMetrics,
    TokenUsage, StatusBreakdown
)

class AnalyticsService:
    """
    Analytics service that provides high-level analytics operations
    by orchestrating database queries and transforming results into
    structured Pydantic models for API consumption.
    """

    def __init__(self):
        """Initialize service without database dependency"""
        self.logger = logging.getLogger(__name__)

    def get_metrics_overview(self, db: Session) -> MetricsOverview:
        """
        Get comprehensive overview of all key metrics.

        Args:
            db: SQLAlchemy database session

        Returns:
            MetricsOverview model with aggregated metrics
        """
        try:
            # Get total conversations
            total = db.execute(text("SELECT COUNT(*) as total FROM conversations")).scalar()

            # Get active conversations (assuming status='active')
            active = db.execute(
                text("SELECT COUNT(*) as active FROM conversations WHERE status = 'active'")
            ).scalar()

            # Get satisfaction stats
            satisfaction_stats = db.execute(
                text("""
                    SELECT satisfaction, COUNT(*) as count
                    FROM conversations
                    GROUP BY satisfaction
                """)
            ).fetchall()

            # Calculate positive satisfaction percentage
            positive_count = next(
                (item['count'] for item in satisfaction_stats if item['satisfaction'] == 'positive'),
                0
            )
            positive_percentage = round((positive_count / total * 100), 2) if total > 0 else 0.0

            # Get token usage
            token_stats = db.execute(
                text("""
                    SELECT
                        SUM(input_tokens) as input_tokens,
                        SUM(output_tokens) as output_tokens
                    FROM conversations
                """)
            ).fetchone()

            # Calculate average tokens
            avg_tokens = (token_stats['input_tokens'] + token_stats['output_tokens']) / total if total > 0 else 0.0

            # Get status breakdown
            status_breakdown = dict(db.execute(
                text("""
                    SELECT status, COUNT(*) as count
                    FROM conversations
                    GROUP BY status
                """)
            ).fetchall())

            return MetricsOverview(
                total_conversations=total,
                active_conversations=active,
                positive_satisfaction=positive_percentage,
                average_tokens=avg_tokens,
                status_breakdown=status_breakdown
            )

        except SQLAlchemyError as e:
            self.logger.error(f"Error getting metrics overview: {e}")
            raise

    def get_conversation_counts(self, db: Session) -> Dict[str, int]:
        """
        Get total conversation counts and status breakdown.

        Args:
            db: SQLAlchemy database session

        Returns:
            Dictionary with total count and status counts
        """
        try:
            # Get total count
            total = db.execute(text("SELECT COUNT(*) as total FROM conversations")).scalar()

            # Get status breakdown
            status_counts = dict(db.execute(
                text("""
                    SELECT status, COUNT(*) as count
                    FROM conversations
                    GROUP BY status
                """)
            ).fetchall())

            # Add total to the result
            result = {"total": total}
            result.update(status_counts)

            return result

        except SQLAlchemyError as e:
            self.logger.error(f"Error getting conversation counts: {e}")
            raise

    def get_satisfaction_metrics(self, db: Session) -> SatisfactionMetrics:
        """
        Get satisfaction score breakdown and percentages.

        Args:
            db: SQLAlchemy database session

        Returns:
            SatisfactionMetrics model with counts and percentages
        """
        try:
            # Get total conversation turns
            total_turns = db.execute(text("SELECT COUNT(*) as total FROM conversations")).scalar()

            # Get satisfaction breakdown
            satisfaction_counts = dict(db.execute(
                text("""
                    SELECT satisfaction, COUNT(*) as count
                    FROM conversations
                    GROUP BY satisfaction
                """)
            ).fetchall())

            # Get individual counts with defaults
            positive_count = satisfaction_counts.get('positive', 0)
            neutral_count = satisfaction_counts.get('neutral', 0)
            negative_count = satisfaction_counts.get('negative', 0)

            # Calculate percentages
            positive_percentage = round((positive_count / total_turns * 100), 2) if total_turns > 0 else 0.0
            neutral_percentage = round((neutral_count / total_turns * 100), 2) if total_turns > 0 else 0.0
            negative_percentage = round((negative_count / total_turns * 100), 2) if total_turns > 0 else 0.0

            return SatisfactionMetrics(
                total_turns=total_turns,
                positive_count=positive_count,
                neutral_count=neutral_count,
                negative_count=negative_count,
                positive_percentage=positive_percentage,
                neutral_percentage=neutral_percentage,
                negative_percentage=negative_percentage
            )

        except SQLAlchemyError as e:
            self.logger.error(f"Error getting satisfaction metrics: {e}")
            raise

    def get_token_usage(self, db: Session) -> TokenUsage:
        """
        Get token usage statistics.

        Args:
            db: SQLAlchemy database session

        Returns:
            TokenUsage model with token statistics
        """
        try:
            # Get total token usage
            token_stats = db.execute(
                text("""
                    SELECT
                        SUM(input_tokens) as input_tokens,
                        SUM(output_tokens) as output_tokens
                    FROM conversations
                """)
            ).fetchone()

            if not token_stats:
                return TokenUsage(
                    total_tokens=0,
                    average_tokens=0.0,
                    max_tokens=0,
                    min_tokens=0
                )

            total_tokens = token_stats['input_tokens'] + token_stats['output_tokens']

            # Get total conversations for average calculation
            total_conversations = db.execute(
                text("SELECT COUNT(*) as total FROM conversations")
            ).scalar()

            # Get min/max tokens
            min_max_stats = db.execute(
                text("""
                    SELECT
                        MIN(input_tokens + output_tokens) as min_tokens,
                        MAX(input_tokens + output_tokens) as max_tokens
                    FROM conversations
                """)
            ).fetchone()

            avg_tokens = total_tokens / total_conversations if total_conversations > 0 else 0.0

            return TokenUsage(
                total_tokens=total_tokens,
                average_tokens=avg_tokens,
                max_tokens=min_max_stats['max_tokens'] or 0,
                min_tokens=min_max_stats['min_tokens'] or 0
            )

        except SQLAlchemyError as e:
            self.logger.error(f"Error getting token usage: {e}")
            raise

    def get_status_breakdown(self, db: Session) -> StatusBreakdown:
        """
        Get conversation status breakdown.

        Args:
            db: SQLAlchemy database session

        Returns:
            StatusBreakdown model with status counts
        """
        try:
            # Get status counts
            status_counts = dict(db.execute(
                text("""
                    SELECT status, COUNT(*) as count
                    FROM conversations
                    GROUP BY status
                """)
            ).fetchall())

            # Map to expected StatusBreakdown model
            active = status_counts.get('active', 0)
            inactive = status_counts.get('inactive', 0)
            ended = status_counts.get('ended', 0)
            other = sum(count for status, count in status_counts.items()
                       if status not in ['active', 'inactive', 'ended'])

            return StatusBreakdown(
                active=active,
                inactive=inactive,
                ended=ended,
                other=other
            )

        except SQLAlchemyError as e:
            self.logger.error(f"Error getting status breakdown: {e}")
            raise

    def get_trends(self, db: Session, period: str = "daily") -> Dict[str, Any]:
        """
        Get time-based trends for conversations.

        Args:
            db: SQLAlchemy database session
            period: Time period ('daily', 'weekly', 'monthly')

        Returns:
            Dictionary with trend data points
        """
        try:
            # Validate period
            if period not in ['daily', 'weekly', 'monthly']:
                raise ValueError("Invalid period. Must be 'daily', 'weekly', or 'monthly'")

            # Build query based on period
            if period == 'daily':
                group_by = "DATE(created_at)"
            elif period == 'weekly':
                group_by = "DATE_TRUNC('week', created_at)"
            else:  # monthly
                group_by = "DATE_TRUNC('month', created_at)"

            query = f"""
                SELECT {group_by} as period, COUNT(*) as count
                FROM conversations
                GROUP BY {group_by}
                ORDER BY period
            """

            trend_data = db.execute(text(query)).fetchall()

            # Convert to list of dictionaries
            return {
                "period": period,
                "data": [{"date": row['period'].isoformat(), "count": row['count']} for row in trend_data]
            }

        except SQLAlchemyError as e:
            self.logger.error(f"Error getting trends: {e}")
            raise
        except ValueError as e:
            self.logger.error(f"Invalid period for trends: {e}")
            raise