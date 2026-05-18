import time
from collections import defaultdict

from app.config import get_settings


class SimpleRateLimiter:
    """In-memory per-key limiter (key = f'{ip}:{instance_id}')."""

    def __init__(self):
        self._hits: dict[str, list[float]] = defaultdict(list)

    def allow(self, key: str) -> bool:
        lim = get_settings().rate_limit_per_minute
        now = time.monotonic()
        window = 60.0
        hits = self._hits[key]
        cutoff = now - window
        while hits and hits[0] < cutoff:
            hits.pop(0)
        if len(hits) >= lim:
            return False
        hits.append(now)
        return True


rate_limiter = SimpleRateLimiter()
