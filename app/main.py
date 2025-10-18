"""FastAPI application with per-project rate limiting."""
from __future__ import annotations

import asyncio
import time
from collections import deque
from typing import Deque, Dict

from fastapi import Depends, FastAPI, Header, HTTPException, status


class RateLimiter:
    """Simple in-memory rate limiter scoped per project identifier."""

    def __init__(self, limit: int, window_seconds: int) -> None:
        self.limit = limit
        self.window_seconds = window_seconds
        self._requests: Dict[str, Deque[float]] = {}
        self._lock = asyncio.Lock()

    async def hit(self, project_id: str) -> None:
        """Record a request for *project_id* and raise if limit exceeded."""
        now = time.monotonic()
        async with self._lock:
            requests = self._requests.setdefault(project_id, deque())
            # Remove timestamps outside the configured window so only recent
            # requests count against the limit.
            while requests and now - requests[0] > self.window_seconds:
                requests.popleft()

            if len(requests) >= self.limit:
                # Reject the request once the per-project quota is exhausted
                # within the rolling window.
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail={
                        "error": "Too Many Requests",
                        "message": "Rate limit exceeded for project",
                        "project_id": project_id,
                    },
                )

            # Store the timestamp for the accepted request so future calls can
            # evaluate the updated usage for this project.
            requests.append(now)


limiter = RateLimiter(limit=10, window_seconds=60)
app = FastAPI(title="FastAPI Rate Limited API")


async def enforce_rate_limit(project_id: str = Header(..., alias="X-Project-ID")) -> str:
    """Dependency that applies the rate limit for the provided project."""
    await limiter.hit(project_id)
    return project_id


@app.get("/your-endpoint")
async def your_endpoint(project_id: str = Depends(enforce_rate_limit)) -> dict[str, str]:
    """Example endpoint that responds only when within the rate limit."""
    return {
        "project_id": project_id,
        "message": "Request successful",
    }
