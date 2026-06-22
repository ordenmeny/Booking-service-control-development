import time
from collections import defaultdict, deque

from fastapi import HTTPException, Request

RATE_LIMIT_REQUESTS = 5
RATE_LIMIT_WINDOW_SECONDS = 60

_requests_by_client: dict[str, deque[float]] = defaultdict(deque)


def check_booking_rate_limit(request: Request) -> None:
    client = request.client.host if request.client else "unknown"
    now = time.monotonic()
    requests = _requests_by_client[client]

    while requests and now - requests[0] > RATE_LIMIT_WINDOW_SECONDS:
        requests.popleft()

    if len(requests) >= RATE_LIMIT_REQUESTS:
        raise HTTPException(
            status_code=429,
            detail="Too many booking requests",
        )

    requests.append(now)


def reset_rate_limit() -> None:
    _requests_by_client.clear()
