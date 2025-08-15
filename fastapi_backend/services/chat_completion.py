"""
Core chat completion service that integrates RAG and feedback pipeline.
"""

import os
import uuid
from uuid import uuid4
import logging
import requests
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel
from sqlalchemy.orm import Session
import hashlib
from sqlalchemy import inspect

from models.schemas import ChatCompletionRequest, ChatCompletionResponse, Message, Choice
from config import settings
from wildfeedback.praise import PraisePipeline
from models.database import get_db, Conversation, ConversationTurn, engine
from services import singletons


def _assert_schema():
    cols = {c["name"] for c in inspect(engine).get_columns("conversations")}
    if "session_id" not in cols:
        raise RuntimeError("DB schema mismatch: conversations.session_id is missing")
    
class ChatCompletionService:
    """
    Service for processing chat completion requests.
    """

    def __init__(self):
        """
        Initialize the chat completion service with RAG and feedback pipeline.
        """
        _assert_schema()

        self.rag = singletons.get_rag()

        self.feedback = singletons.get_feedback()

    def process_request(self, request: ChatCompletionRequest, conversation_id: Optional[int] = None) -> ChatCompletionResponse:
        """
        Process a chat completion request and return a response.

        Args:
            request: The chat completion request
            conversation_id: Optional conversation ID to continue an existing conversation

        Returns:
            The chat completion response
        """
        # Get the last user message
        user_message = None
        for message in reversed(request.messages):
            if message.role == "user":
                user_message = message
                break

        if not user_message:
            raise ValueError("No user message found in the conversation")

        # Process the request
        response = self._process_chat_completion(request, conversation_id)

        # Save the conversation to database
        self._save_conversation_to_db(request, response, conversation_id)

        return response

    def _process_chat_completion(self, request: ChatCompletionRequest, conversation_id: Optional[int] = None) -> ChatCompletionResponse:
        """
        Process the chat completion request and return a response.

        Args:
            request: The chat completion request
            conversation_id: Optional conversation ID to continue an existing conversation

        Returns:
            The chat completion response
        """
        # Get the last user message
        user_message = None
        for message in reversed(request.messages):
            if message.role == "user":
                user_message = message
                break

        if not user_message:
            raise ValueError("No user message found in the conversation")

        # Get conversation history if available
        conversation_history = []
        if conversation_id:
            from services.conversation_service import ConversationService
            conversation_service = ConversationService()
            conversation_history = conversation_service.get_conversation_history(conversation_id)

        # RAG retrieval
        docs = self.rag.query(user_message.content)
        context = "\n".join([doc["content"] for doc in docs])

        # Include conversation history in context
        history_context = "\n".join([f"[{turn.role}]: {turn.content}" for turn in conversation_history])
        full_prompt = f"[CONTEXT]\n{context}\n[HISTORY]\n{history_context}\n[USER]\n{user_message.content}"

        # Call LM Studio endpoint
        ai_reply = self._query_ai(full_prompt, request)

        # Classify feedback
        sat_dsat = None
        try:
            feedback_result = self.feedback.classify(user_message.content)
            sat_dsat = max(feedback_result, key=feedback_result.get)
        except Exception as e:
            logging.error(f"Feedback classification error: {e}")

        # Format response
        response = ChatCompletionResponse(
            id=str(conversation_id) if conversation_id else str(uuid4()),
            object="chat.completion",
            created=int(datetime.utcnow().timestamp()),
            model=request.model,
            choices=[
                Choice(
                    index=0,
                    message=Message(
                        role="assistant",
                        content=ai_reply
                    ),
                    finish_reason="stop"
                )
            ]
        )

        return response

    def _query_ai(self, prompt: str, request: ChatCompletionRequest) -> str:
        """
        Query the AI model endpoint.
        """
        headers = {"Content-Type": "application/json"}
        payload = {
            "model": request.model or settings.DEFAULT_MODEL,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": request.max_tokens or settings.DEFAULT_MAX_TOKENS,
            "temperature": request.temperature or settings.DEFAULT_TEMPERATURE,
        }

        try:
            resp = requests.post(
                settings.LMSTUDIO_ENDPOINT,
                headers=headers,
                json=payload,
                timeout=30
            )
            resp.raise_for_status()
            data = resp.json()
            return data["choices"][0]["message"]["content"].strip()
        except Exception as e:
            logging.error(f"AI query error: {e}")
            return f"[Error contacting AI: {e}]"

    def _save_conversation_to_db(self, request: ChatCompletionRequest, response: ChatCompletionResponse, conversation_id: Optional[int] = None):
        """
        Save the conversation to the database.

        Args:
            request: The chat completion request
            response: The chat completion response
            conversation_id: Optional conversation ID to continue an existing conversation
        """
        db: Session = next(get_db())

        try:
            if conversation_id:
                # Continue existing conversation
                conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
                if not conversation:
                    # Create new conversation if ID is invalid
                    conversation = Conversation(
                        model=request.model,
                        extra_data={"request": request.dict()}
                    )
                    db.add(conversation)
                    db.commit()
                    db.refresh(conversation)
            else:
                # Create new conversation
                conversation = Conversation(
                    model=request.model,
                    extra_data={"request": request.dict()}
                )

                db.add(conversation)
                db.commit()
                db.refresh(conversation)

            # Save each message as a turn
            for i, message in enumerate(request.messages):
                # Check for duplicate message
                message_hash = hashlib.sha256(f"{message.role}:{message.content}".encode()).hexdigest()
                existing_turn = db.query(ConversationTurn).filter(
                    ConversationTurn.conversation_id == conversation.id,
                    ConversationTurn.message_hash == message_hash
                ).first()

                if not existing_turn:
                    turn = ConversationTurn(
                        conversation_id=conversation.id,
                        role=message.role,
                        content=message.content,
                        message_hash=message_hash,
                        # Add satisfaction score for user messages
                        satisfaction_score=None if message.role != "user" else "Neutral",
                        extra_data={"index": i}
                    )
                    db.add(turn)

            # Save assistant response
            assistant_message_hash = hashlib.sha256(f"assistant:{response.choices[0].message.content}".encode()).hexdigest()
            existing_assistant_turn = db.query(ConversationTurn).filter(
                ConversationTurn.conversation_id == conversation.id,
                ConversationTurn.message_hash == assistant_message_hash
            ).first()

            if not existing_assistant_turn:
                assistant_turn = ConversationTurn(
                    conversation_id=conversation.id,
                    role="assistant",
                    content=response.choices[0].message.content,
                    message_hash=assistant_message_hash,
                    extra_data={"response_id": response.id}
                )
                db.add(assistant_turn)

            db.commit()
        except Exception as e:
            db.rollback()
            logging.error(f"Database error: {e}")
        finally:
            db.close()