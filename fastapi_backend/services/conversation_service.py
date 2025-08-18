"""Conversation management service for maintaining conversation state and history."""
import logging
from typing import Optional, List, Dict, Any
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from models.database import get_db, Conversation, ConversationTurn
from models.schemas import Message, ConversationTurn as ConversationTurnSchema
import hashlib
from datetime import datetime


class ConversationService:
    """Service for managing conversations and their state."""

    def __init__(self):
        """Initialize the conversation service."""
        self.logger = logging.getLogger(__name__)

    def create_conversation(
        self,
        model: str,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
    ) -> Conversation:
        """
        Create a new conversation with a unique session ID.
        """
        db: Session = next(get_db())
        try:
            conversation = Conversation(
                model=model,
                user_id=user_id,
                session_id=session_id,  # ✅ Store it in the DB
            )
            db.add(conversation)
            db.commit()
            db.refresh(conversation)
            return conversation
        except SQLAlchemyError as e:
            db.rollback()
            self.logger.error(f"Error creating conversation: {e}")
            raise
        finally:
            db.close()

    def get_conversation_by_id(self, conversation_id: int) -> Optional[Conversation]:
        """
        Retrieve a conversation by its ID.

        Args:
            conversation_id: The ID of the conversation to retrieve

        Returns:
            The conversation object if found, None otherwise
        """
        db: Session = next(get_db())
        try:
            return (
                db.query(Conversation)
                .filter(Conversation.id == conversation_id)
                .first()
            )
        except SQLAlchemyError as e:
            self.logger.error(f"Error retrieving conversation: {e}")
            return None
        finally:
            db.close()

    def get_conversation_by_session(self, session_id: str) -> Optional[Conversation]:
        """
        Retrieve a conversation by its session ID.

        Args:
            session_id: The session ID of the conversation to retrieve

        Returns:
            The conversation object if found, None otherwise
        """
        db: Session = next(get_db())
        try:
            return (
                db.query(Conversation)
                .filter(Conversation.session_id == session_id)
                .first()
            )
        except SQLAlchemyError as e:
            self.logger.error(f"Error retrieving conversation by session: {e}")
            return None
        finally:
            db.close()

    def _generate_message_hash(self, message: str, role: str) -> str:
        """
        Generate a hash for a message to detect duplicates.
        """
        return hashlib.sha256(f"{role}:{message}".encode()).hexdigest()

    def add_message_to_conversation(
        self, conversation_id: int, message: Message
    ) -> ConversationTurn:
        """
        Add a message to an existing conversation with deduplication.

        Args:
            conversation_id: The ID of the conversation to add the message to
            message: The message to add

        Returns:
            The created conversation turn object

        Raises:
            ValueError: If conversation not found or message is empty
            SQLAlchemyError: If database error occurs
        """
        if not message.content or not message.content.strip():
            raise ValueError("Message content cannot be empty")

        db: Session = next(get_db())
        try:
            # Get the conversation
            conversation = (
                db.query(Conversation)
                .filter(Conversation.id == conversation_id)
                .first()
            )
            if not conversation:
                raise ValueError(f"Conversation with ID {conversation_id} not found")

            # Check for duplicate message
            message_hash = self._generate_message_hash(message.content, message.role)
            existing_turn = (
                db.query(ConversationTurn)
                .filter(
                    ConversationTurn.conversation_id == conversation_id,
                    ConversationTurn.message_hash == message_hash,
                )
                .first()
            )

            if existing_turn:
                self.logger.warning(
                    f"Duplicate message detected, using existing turn: {existing_turn.id}"
                )
                return existing_turn

            # Create the conversation turn
            turn = ConversationTurn(
                conversation_id=conversation_id,
                role=message.role,
                content=message.content,
                message_hash=message_hash,
                extra_data={"index": len(conversation.turns)},
            )

            db.add(turn)
            db.commit()
            db.refresh(turn)

            # Update conversation metadata
            conversation.total_tokens = (conversation.total_tokens or 0) + (
                len(message.content.split()) or 0
            )
            conversation.updated_at = datetime.utcnow()
            db.commit()

            return turn
        except SQLAlchemyError as e:
            db.rollback()
            self.logger.error(f"Database error adding message to conversation: {e}")
            raise
        except Exception as e:
            db.rollback()
            self.logger.error(f"Error adding message to conversation: {e}")
            raise
        finally:
            db.close()

    def get_conversation_history(
        self, conversation_id: int
    ) -> List[ConversationTurnSchema]:
        """
        Retrieve complete message history for a conversation.

        Args:
            conversation_id: The ID of the conversation to retrieve history for

        Returns:
            List of conversation turns (messages) in the conversation

        Raises:
            ValueError: If conversation not found
        """
        db: Session = next(get_db())
        try:
            # Get the conversation
            conversation = (
                db.query(Conversation)
                .filter(Conversation.id == conversation_id)
                .first()
            )
            if not conversation:
                raise ValueError(f"Conversation with ID {conversation_id} not found")

            # Get all turns for this conversation
            turns = (
                db.query(ConversationTurn)
                .filter(ConversationTurn.conversation_id == conversation_id)
                .order_by(ConversationTurn.created_at)
                .all()
            )

            # Convert to schema objects
            return [ConversationTurnSchema.from_orm(turn) for turn in turns]
        except SQLAlchemyError as e:
            self.logger.error(f"Error retrieving conversation history: {e}")
            raise
        finally:
            db.close()

    def end_conversation(self, conversation_id: int) -> bool:
        """
        Mark a conversation as ended.

        Args:
            conversation_id: The ID of the conversation to end

        Returns:
            True if successful, False otherwise
        """
        db: Session = next(get_db())
        try:
            conversation = (
                db.query(Conversation)
                .filter(Conversation.id == conversation_id)
                .first()
            )
            if not conversation:
                return False

            conversation.is_active = False
            conversation.status = "ended"
            db.commit()
            return True
        except SQLAlchemyError as e:
            db.rollback()
            self.logger.error(f"Error ending conversation: {e}")
            return False
        finally:
            db.close()

    def get_or_create_conversation(
        self, session_id: Optional[str] = None, model: Optional[str] = None
    ) -> Conversation:
        if session_id:
            conversation = self.get_conversation_by_session(session_id)
            if conversation:
                return conversation

        if not model:
            raise ValueError("Model must be provided to create new conversation")

        # ✅ Pass session_id when creating
        return self.create_conversation(model=model, session_id=session_id)

    def update_conversation(
        self, conversation_id: int, update_data: Dict[str, Any]
    ) -> Optional[Conversation]:
        """
        Update a conversation with new data.

        Args:
            conversation_id: The ID of the conversation to update
            update_data: Dictionary containing fields to update

        Returns:
            The updated conversation object if successful, None otherwise
        """
        db: Session = next(get_db())
        try:
            conversation = (
                db.query(Conversation)
                .filter(Conversation.id == conversation_id)
                .first()
            )
            if not conversation:
                return None

            # Update fields based on provided data
            if "model" in update_data:
                conversation.model = update_data["model"]
            if "status" in update_data:
                conversation.status = update_data["status"]
            if "is_active" in update_data:
                conversation.is_active = update_data["is_active"]
            if "extra_data" in update_data:
                conversation.extra_data = update_data["extra_data"]

            db.commit()
            db.refresh(conversation)
            return conversation
        except SQLAlchemyError as e:
            db.rollback()
            self.logger.error(f"Error updating conversation: {e}")
            return None
        finally:
            db.close()

    def delete_conversation(self, conversation_id: int) -> bool:
        """
        Delete a conversation and all its associated turns.

        Args:
            conversation_id: The ID of the conversation to delete

        Returns:
            True if successful, False otherwise
        """
        db: Session = next(get_db())
        try:
            # First delete all turns associated with this conversation
            db.query(ConversationTurn).filter(
                ConversationTurn.conversation_id == conversation_id
            ).delete()

            # Then delete the conversation itself
            result = (
                db.query(Conversation)
                .filter(Conversation.id == conversation_id)
                .delete()
            )
            if result == 0:
                return False

            db.commit()
            return True
        except SQLAlchemyError as e:
            db.rollback()
            self.logger.error(f"Error deleting conversation: {e}")
            return False
        finally:
            db.close()
