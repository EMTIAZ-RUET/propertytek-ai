"""
Redis-backed chat history service.
Stores and retrieves the last N chat messages per user.
"""

from typing import List, Dict, Any
import json
import redis
from config.settings import settings


class ChatHistoryService:
    def __init__(self):
        self.client = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_DB,
            password=settings.REDIS_PASSWORD,
            decode_responses=True,
        )

    def _key(self, user_id: str) -> str:
        return f"chat:history:{user_id}"

    def get_last_messages(self, user_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        if not user_id:
            return []
        key = self._key(user_id)
        # Get the last 'limit' items from the list
        raw = self.client.lrange(key, -limit, -1) or []
        messages = []
        for item in raw:
            try:
                messages.append(json.loads(item))
            except Exception:
                continue
        return messages

    def append_message(self, user_id: str, role: str, content: str) -> None:
        if not user_id:
            return
        key = self._key(user_id)
        payload = json.dumps({"role": role, "content": content})
        self.client.rpush(key, payload)
        # Optional: cap list length to 200 messages
        self.client.ltrim(key, -200, -1)


