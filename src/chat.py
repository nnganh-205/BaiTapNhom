import os
from urllib.parse import urlsplit, urlunsplit

import requests
from flask import Blueprint, jsonify, request

chat_bp = Blueprint("chat", __name__)

CHATBOT_API_URL = os.getenv("CHATBOT_API_URL", "http://127.0.0.1:8001/chat")
CHATBOT_TIMEOUT = int(os.getenv("CHATBOT_TIMEOUT", "30"))
CHAT_HISTORY_LIMIT = int(os.getenv("CHAT_HISTORY_LIMIT", "40"))


def _normalize_chat_url(url: str) -> str:
    """Ensure upstream chatbot URL points to POST /chat endpoint."""
    cleaned = (url or "").strip() or "http://127.0.0.1:8001/chat"
    parsed = urlsplit(cleaned)

    if not parsed.scheme or not parsed.netloc:
        return "http://127.0.0.1:8001/chat"

    path = parsed.path.rstrip("/")
    if path in {"", "/"}:
        path = "/chat"
    elif path.endswith("/api/chat"):
        path = path[: -len("/api/chat")] + "/chat"

    return urlunsplit((parsed.scheme, parsed.netloc, path, parsed.query, parsed.fragment))


def _candidate_chat_urls() -> list[str]:
    primary = _normalize_chat_url(CHATBOT_API_URL)
    defaults = [
        "http://127.0.0.1:8001/chat",
        "http://127.0.0.1:8000/chat",
    ]

    ordered = [primary] + defaults
    deduped = []
    seen = set()
    for item in ordered:
        normalized = _normalize_chat_url(item)
        if normalized not in seen:
            seen.add(normalized)
            deduped.append(normalized)
    return deduped


def _local_chat_fallback(payload: dict, reason: str):
    """Fallback to local chatbot module when upstream service is unreachable/misrouted."""
    try:
        from ai_chatbot.chatbot import chat_once
        from ai_chatbot.databases.sqlite_db import (
            get_thread_messages,
            save_message,
            save_thread,
            update_thread_access,
        )

        user_id = payload["user_id"]
        session_id = payload["chat_session_id"]
        query = payload["new_query"]

        save_thread(user_id, session_id)
        save_message(user_id, session_id, "user", query)
        history = get_thread_messages(user_id, session_id, limit=CHAT_HISTORY_LIMIT)

        answer = chat_once(user_id, session_id, query, history)

        save_message(user_id, session_id, "assistant", answer)
        update_thread_access(user_id, session_id)

        return (
            jsonify(
                {
                    "answer": answer,
                    "source": "local_fallback",
                    "fallback_reason": reason,
                }
            ),
            200,
        )
    except Exception as exc:  # noqa: BLE001
        return jsonify({"detail": f"Khong the dung local fallback: {exc}"}), 503


@chat_bp.post("/api/chat")
def proxy_chat():
    payload = request.get_json(silent=True)
    if not payload:
        return jsonify({"detail": "Request body trong."}), 400

    required_fields = ("user_id", "chat_session_id", "new_query")
    normalized = {}
    for field in required_fields:
        value = str(payload.get(field, "")).strip()
        if not value:
            return jsonify({"detail": f"Thieu hoac rong: {field}"}), 400
        normalized[field] = value

    last_error = None
    last_status = None

    for upstream_url in _candidate_chat_urls():
        try:
            response = requests.post(upstream_url, json=normalized, timeout=CHATBOT_TIMEOUT)
            if response.status_code == 404:
                last_error = f"Upstream 404 at {upstream_url}"
                last_status = 404
                continue

            response.raise_for_status()
            return jsonify(response.json()), response.status_code

        except requests.exceptions.ConnectionError:
            last_error = f"Khong ket noi duoc chatbot service tai {upstream_url}."
            last_status = 503
            continue
        except requests.exceptions.Timeout:
            last_error = f"Chatbot phan hoi cham tai {upstream_url}, vui long thu lai."
            last_status = 504
            continue
        except requests.exceptions.HTTPError as exc:
            try:
                detail = exc.response.json()
            except Exception:
                detail = {"detail": "Loi tu chatbot service."}
            return jsonify(detail), exc.response.status_code
        except Exception as exc:  # noqa: BLE001
            return jsonify({"detail": f"Loi khong xac dinh: {exc}"}), 500

    if last_status == 404:
        return _local_chat_fallback(
            normalized,
            "upstream_404_endpoint_mismatch",
        )

    if last_status in {503, 504}:
        return _local_chat_fallback(
            normalized,
            "upstream_unavailable",
        )

    return jsonify({"detail": last_error or "Khong ket noi duoc chatbot service."}), last_status or 503

