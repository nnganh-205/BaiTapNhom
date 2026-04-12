import logging
import time
import uuid
from contextlib import asynccontextmanager
import os

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, field_validator

from ai_chatbot.chatbot import chat_once
from ai_chatbot.databases.sqlite_db import (
    get_thread_messages,
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


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


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

