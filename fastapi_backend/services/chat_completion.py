"""
Core chat completion service that integrates RAG and feedback pipeline.
"""

import os
import uuid
import logging
import requests
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel
from sqlalchemy.orm import Session

from models.schemas import ChatCompletionRequest, ChatCompletionResponse, Message, Choice
from config import settings
from RAG.main import RAG
from wildfeedback.praise import PraisePipeline
from models.database import get_db, Conversation, ConversationTurn

class ChatCompletionService:
    """
    Service for processing chat completion requests.
    """

    def __init__(self):
        """
        Initialize the chat completion service with RAG and feedback pipeline.
        """
        # Initialize RAG system
        self.rag = RAG(docs_path=settings.RAG_DOCS_PATH)

        # Initialize feedback pipeline
        self.feedback = PraisePipeline(
            strategy_file=settings.FEEDBACK_STRATEGY_PATH,
            classifier_file=settings.FEEDBACK_CLASSIFIER_PATH
        )

    def process_request(self, request: ChatCompletionRequest) -> ChatCompletionResponse:
        """
        Process a chat completion request and return a response.
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
        response = self._process_chat_completion(request)

        # Save the conversation to database
        self._save_conversation_to_db(request, response)

        return response

    def _process_chat_completion(self, request: ChatCompletionRequest) -> ChatCompletionResponse:
        """
        Process the chat completion request and return a response.
        """
        # Get the last user message
        user_message = None
        for message in reversed(request.messages):
            if message.role == "user":
                user_message = message
                break

        if not user_message:
            raise ValueError("No user message found in the conversation")

        # RAG retrieval
        docs = self.rag.query(user_message.content)
        context = "\n".join([doc["content"] for doc in docs])
        prompt = f"[CONTEXT]\n{context}\n[USER]\n{user_message.content}"

        # Call LM Studio endpoint
        ai_reply = self._query_ai(prompt, request)

        # Classify feedback
        sat_dsat = None
        try:
            feedback_result = self.feedback.classify(user_message.content)
            sat_dsat = max(feedback_result, key=feedback_result.get)
        except Exception as e:
            logging.error(f"Feedback classification error: {e}")

        # Format response
        response = ChatCompletionResponse(
            id=str(uuid.uuid4()),
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

    def _save_conversation_to_db(self, request: ChatCompletionRequest, response: ChatCompletionResponse):
        """
        Save the conversation to the database.
        """
        db: Session = next(get_db())

        try:
            # Create conversation
            conversation = Conversation(
                model=request.model,
                extra_data={"request": request.dict()}
            )

            db.add(conversation)
            db.commit()
            db.refresh(conversation)

            # Save each message as a turn
            for i, message in enumerate(request.messages):
                turn = ConversationTurn(
                    conversation_id=conversation.id,
                    role=message.role,
                    content=message.content,
                    # Add satisfaction score for user messages
                    satisfaction_score=None if message.role != "user" else "Neutral",
                    extra_data={"index": i}
                )
                db.add(turn)

            # Save assistant response
            assistant_turn = ConversationTurn(
                conversation_id=conversation.id,
                role="assistant",
                content=response.choices[0].message.content,
                extra_data={"response_id": response.id}
            )
            db.add(assistant_turn)

            db.commit()
        except Exception as e:
            db.rollback()
            logging.error(f"Database error: {e}")
        finally:
            db.close()