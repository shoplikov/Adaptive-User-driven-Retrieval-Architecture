"""Periodic metrics service that fetches data from AURA chatbot and saves to analytics database."""
import logging
from typing import Dict, Any, List
from sqlalchemy import create_engine, text, Column, String, Integer, DateTime, Boolean, Float, JSON, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import os
import sys

# Add the analytics-backend directory to Python path
analytics_backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, analytics_backend_dir)

# Add fastapi_backend directory for cross-service imports
fastapi_backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'fastapi_backend'))
sys.path.insert(0, fastapi_backend_dir)

# Import settings with specific module paths to avoid conflicts
import sys
import importlib.util

# Import analytics settings directly
spec = importlib.util.spec_from_file_location("analytics_config", os.path.join(analytics_backend_dir, "config", "settings.py"))
analytics_config_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(analytics_config_module)
analytics_settings = analytics_config_module.settings

# Import fastapi settings directly
spec = importlib.util.spec_from_file_location("fastapi_config", os.path.join(fastapi_backend_dir, "config", "__init__.py"))
fastapi_config_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fastapi_config_module)
fastapi_settings = fastapi_config_module.settings

# Database base classes
Base = declarative_base()

# Logger setup
logger = logging.getLogger(__name__)

class MetricsService:
    """
    Service that periodically fetches conversation data from AURA chatbot,
    calculates metrics, and saves them to the analytics database.
    """

    def __init__(self):
        """Initialize the metrics service with database connections."""
        self.logger = logging.getLogger(__name__)

        # Connect to fastapi_backend database
        self.fastapi_engine = create_engine(
            f"postgresql://{fastapi_settings.POSTGRES_USER}:{fastapi_settings.POSTGRES_PASSWORD}@"
            f"{fastapi_settings.POSTGRES_HOST}:{fastapi_settings.POSTGRES_PORT}/{fastapi_settings.POSTGRES_DB}"
        )
        self.fastapi_session = sessionmaker(bind=self.fastapi_engine)

        # Connect to analytics database
        self.analytics_engine = create_engine(analytics_settings.ANALYTICS_DATABASE_URL)
        self.analytics_session = sessionmaker(bind=self.analytics_engine)

        self.logger.info("Metrics service initialized with database connections")

    def fetch_conversation_data(self) -> List[Dict[str, Any]]:
        """
        Fetch conversation data from the fastapi_backend database.

        Returns:
            List of conversation dictionaries with relevant data
        """
        session = self.fastapi_session()
        try:
            # Fetch all conversations with their turns
            query = """
            SELECT
                c.id as conversation_id,
                c.session_id,
                c.model,
                c.status,
                c.created_at,
                c.updated_at,
                c.total_tokens,
                c.is_active,
                t.id as turn_id,
                t.role,
                t.content,
                t.tokens,
                t.satisfaction_score,
                t.satisfaction_confidence,
                t.created_at as turn_created_at
            FROM conversations c
            LEFT JOIN conversation_turns t ON c.id = t.conversation_id
            """
            result = session.execute(text(query))
            conversations = []

            # Group turns by conversation
            current_conversation = None
            for row in result:
                # Convert SQLAlchemy result row to dictionary properly
                try:
                    # Try the _asdict() method first (works with newer SQLAlchemy)
                    if hasattr(row, '_asdict'):
                        row_dict = row._asdict()
                    # Try accessing as mapping (works with SQLAlchemy result rows)
                    elif hasattr(row, '_mapping'):
                        row_dict = dict(row._mapping)
                    # Fallback to manual key-value extraction
                    else:
                        row_dict = {key: getattr(row, key) for key in row.keys()}
                except Exception as conversion_error:
                    self.logger.error(f"Error converting row to dict: {conversion_error}")
                    self.logger.error(f"Row object: {row}")
                    raise
                conversation_id = row_dict['conversation_id']

                if not current_conversation or current_conversation['id'] != conversation_id:
                    if current_conversation:
                        conversations.append(current_conversation)
                    current_conversation = {
                        'id': conversation_id,
                        'session_id': row_dict['session_id'],
                        'model': row_dict['model'],
                        'status': row_dict['status'],
                        'created_at': row_dict['created_at'],
                        'updated_at': row_dict['updated_at'],
                        'total_tokens': row_dict['total_tokens'],
                        'is_active': row_dict['is_active'],
                        'turns': []
                    }

                # Add turn if it exists
                if row_dict['turn_id'] is not None:
                    turn = {
                        'id': row_dict['turn_id'],
                        'role': row_dict['role'],
                        'content': row_dict['content'],
                        'tokens': row_dict['tokens'],
                        'satisfaction_score': row_dict['satisfaction_score'],
                        'satisfaction_confidence': row_dict['satisfaction_confidence'],
                        'created_at': row_dict['turn_created_at']
                    }
                    current_conversation['turns'].append(turn)

            # Add the last conversation
            if current_conversation:
                conversations.append(current_conversation)

            self.logger.info(f"Fetched {len(conversations)} conversations")
            return conversations

        except Exception as e:
            self.logger.error(f"Error fetching conversation data: {e}")
            raise
        finally:
            session.close()

    def calculate_metrics(self, conversations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calculate metrics from conversation data.

        Args:
            conversations: List of conversation dictionaries

        Returns:
            Dictionary with calculated metrics
        """
        if not conversations:
            return {
                'total_conversations': 0,
                'active_conversations': 0,
                'ended_conversations': 0,
                'total_turns': 0,
                'total_tokens': 0,
                'positive_satisfaction': 0,
                'neutral_satisfaction': 0,
                'negative_satisfaction': 0,
                'average_tokens_per_conversation': 0.0,
                'average_tokens_per_turn': 0.0
            }

        total_conversations = len(conversations)
        active_conversations = sum(1 for c in conversations if c['is_active'])
        ended_conversations = sum(1 for c in conversations if c['status'] == 'ended')

        total_turns = sum(len(c['turns']) for c in conversations)
        total_tokens = sum(c.get('total_tokens', 0) for c in conversations)

        positive_satisfaction = 0
        neutral_satisfaction = 0
        negative_satisfaction = 0

        for conversation in conversations:
            for turn in conversation['turns']:
                score = turn.get('satisfaction_score')
                if score == 'SAT':
                    positive_satisfaction += 1
                elif score == 'Neutral':
                    neutral_satisfaction += 1
                elif score == 'DSAT':
                    negative_satisfaction += 1

        average_tokens_per_conversation = total_tokens / total_conversations if total_conversations > 0 else 0.0
        average_tokens_per_turn = total_tokens / total_turns if total_turns > 0 else 0.0

        return {
            'total_conversations': total_conversations,
            'active_conversations': active_conversations,
            'ended_conversations': ended_conversations,
            'total_turns': total_turns,
            'total_tokens': total_tokens,
            'positive_satisfaction': positive_satisfaction,
            'neutral_satisfaction': neutral_satisfaction,
            'negative_satisfaction': negative_satisfaction,
            'average_tokens_per_conversation': average_tokens_per_conversation,
            'average_tokens_per_turn': average_tokens_per_turn
        }

    def save_metrics_to_analytics(self, metrics: Dict[str, Any]) -> bool:
        """
        Save calculated metrics to the analytics database.

        Args:
            metrics: Dictionary with metrics to save

        Returns:
            True if successful, False otherwise
        """
        session = self.analytics_session()
        try:
            # Create a new analytics record
            query = """
            INSERT INTO conversations (
                satisfaction,
                input_tokens,
                output_tokens,
                status,
                created_at,
                updated_at
            ) VALUES (
                :satisfaction,
                :input_tokens,
                :output_tokens,
                :status,
                :created_at,
                :updated_at
            )
            """
            params = {
                'satisfaction': 'positive',  # Default value
                'input_tokens': metrics['total_tokens'],
                'output_tokens': metrics['total_tokens'],  # Assuming same for simplicity
                'status': 'active',  # Default status
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow()
            }

            session.execute(text(query), params)
            session.commit()
            self.logger.info("Metrics saved to analytics database successfully")
            return True

        except Exception as e:
            session.rollback()
            self.logger.error(f"Error saving metrics to analytics database: {e}")
            return False
        finally:
            session.close()

    def run_periodic_task(self):
        """
        Run the periodic task: fetch, calculate, and save metrics.
        """
        self.logger.info("Starting periodic metrics task")
        try:
            # Step 1: Fetch conversation data
            conversations = self.fetch_conversation_data()
            self.logger.info(f"Fetched {len(conversations)} conversations")

            # Step 2: Calculate metrics
            metrics = self.calculate_metrics(conversations)
            self.logger.info(f"Calculated metrics: {metrics}")

            # Step 3: Save metrics to analytics database
            success = self.save_metrics_to_analytics(metrics)
            if success:
                self.logger.info("Periodic metrics task completed successfully")
            else:
                self.logger.error("Failed to save metrics to analytics database")

        except Exception as e:
            self.logger.error(f"Error during periodic metrics task: {e}")