"""
Search Session Service
Persists per-user property search filters across chat turns using Redis.
"""

from typing import Dict, Any, Optional
import json
import redis
from config.settings import settings


class SearchSessionService:
    def __init__(self):
        self.client = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_DB,
            password=settings.REDIS_PASSWORD,
            decode_responses=True,
        )

    def _key(self, user_id: str) -> str:
        return f"search:filters:{user_id}"

    def get_filters(self, user_id: Optional[str]) -> Dict[str, Any]:
        if not user_id:
            return {}
        raw = self.client.get(self._key(user_id))
        if not raw:
            return {}
        try:
            data = json.loads(raw)
            if isinstance(data, dict):
                return data
            return {}
        except Exception:
            return {}

    def set_filters(self, user_id: Optional[str], filters: Optional[Dict[str, Any]]) -> None:
        if not user_id:
            return
        to_store = json.dumps(filters or {})
        self.client.set(self._key(user_id), to_store)


