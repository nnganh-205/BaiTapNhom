import logging
import time
import uuid
from contextlib import asynccontextmanager
from typing import List
import os

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, field_validator

from ai_chatbot.chatbot import chat_once
from ai_chatbot.databases.sqlite_db import (
    get_thread_messages,
    get_user_threads,
    init_db,
    save_message,
    save_thread,
    update_thread_access,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("invenstory_chat_api")


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    yield


app = FastAPI(title="InvenStory AI Chat API", version="1.0.0", lifespan=lifespan)
CHAT_HISTORY_LIMIT = int(os.getenv("CHAT_HISTORY_LIMIT", "40"))


class ChatRequest(BaseModel):
    user_id: str = Field(..., min_length=1, max_length=128)
    chat_session_id: str = Field(..., min_length=1, max_length=128)
    new_query: str = Field(..., min_length=1, max_length=4000)

    @field_validator("user_id", "chat_session_id", "new_query")
    @classmethod
    def validate_non_empty(cls, value: str) -> str:
        trimmed = value.strip()
        if not trimmed:
            raise ValueError("must not be empty")
        return trimmed


class ChatResponse(BaseModel):
    answer: str


class ThreadInfo(BaseModel):
    chat_session_id: str
    created_at: str
    updated_at: str
    is_active: int


class ThreadMessages(BaseModel):
    messages: List[dict]


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.get("/threads/{user_id}", response_model=List[ThreadInfo])
def get_threads(user_id: str) -> List[ThreadInfo]:
    """Get all chat sessions for a user."""
    try:
        threads = get_user_threads(user_id)
        return [ThreadInfo(**thread) for thread in threads]
    except Exception as exc:
        logger.exception("get_threads_failure user_id=%s error=%s", user_id, exc)
        raise HTTPException(status_code=500, detail="Internal server error") from exc


@app.get("/threads/{user_id}/{chat_session_id}", response_model=ThreadMessages)
def get_thread_messages_endpoint(user_id: str, chat_session_id: str) -> ThreadMessages:
    """Get all messages from a chat session."""
    try:
        messages = get_thread_messages(user_id, chat_session_id)
        return ThreadMessages(messages=messages)
    except Exception as exc:
        logger.exception(
            "get_thread_messages_failure user_id=%s session=%s error=%s",
            user_id,
            chat_session_id,
            exc,
        )
        raise HTTPException(status_code=500, detail="Internal server error") from exc


@app.post("/chat", response_model=ChatResponse)
def chat(payload: ChatRequest) -> ChatResponse:
    request_id = str(uuid.uuid4())
    started_at = time.perf_counter()

    try:
        save_thread(payload.user_id, payload.chat_session_id)
        save_message(payload.user_id, payload.chat_session_id, "user", payload.new_query)

        history = get_thread_messages(payload.user_id, payload.chat_session_id, limit=CHAT_HISTORY_LIMIT)
        answer = chat_once(payload.user_id, payload.chat_session_id, payload.new_query, history)

        save_message(payload.user_id, payload.chat_session_id, "assistant", answer)
        update_thread_access(payload.user_id, payload.chat_session_id)

        latency_ms = (time.perf_counter() - started_at) * 1000
        logger.info(
            "chat_success request_id=%s user_id=%s session=%s latency_ms=%.2f",
            request_id,
            payload.user_id,
            payload.chat_session_id,
            latency_ms,
        )
        return ChatResponse(answer=answer)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:  # noqa: BLE001
        logger.exception("chat_failure request_id=%s error=%s", request_id, exc)
        raise HTTPException(status_code=500, detail="Internal server error") from exc

