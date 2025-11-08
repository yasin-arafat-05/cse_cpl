import time
import logging
import asyncio
from typing import Dict, Tuple
from starlette.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, Request, HTTPException


# ====================== Disable default uvicorn logging ======================
logger = logging.getLogger("uvicorn.access")
logger.disabled = True
app_logger = logging.getLogger("my_fastapi_app")


# ====================== Fixed Window Rate Limiter ======================
class FixedWindowRateLimiter:
    def __init__(self, max_requests: int, window_seconds: float = 1.0):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.ip_to_window: Dict[str, Tuple[int, int]] = {}
        self._lock = asyncio.Lock()

    async def allow(self, key: str) -> Tuple[bool, int]:
        now_window = int(time.time())
        async with self._lock:
            window_start, count = self.ip_to_window.get(key, (now_window, 0))
            if window_start != now_window:
                window_start = now_window
                count = 0
            if count < self.max_requests:
                count += 1
                self.ip_to_window[key] = (window_start, count)
                remaining = self.max_requests - count
                return True, remaining
            else:
                remaining = 0
                return False, remaining


# ====================== Concurrent Upload Limiter ======================
MAX_CONCURRENT_UPLOADS = 2
upload_semaphore = asyncio.Semaphore(MAX_CONCURRENT_UPLOADS)


# ====================== Middleware Registration ======================
def register_middleware(app: FastAPI):
    rate_limiter = FixedWindowRateLimiter(max_requests=100, window_seconds=1.0)

    @app.middleware("http")
    async def custom_logging(req: Request, call_next):
        start_time = time.time()
        client_ip = getattr(req.client, "host", "unknown")
        allowlisted_paths = {"/", "/health", "/docs", "/openapi.json"}

        try:
            # ---------- Rate limiting check ----------
            if req.url.path not in allowlisted_paths:
                allowed, remaining = await rate_limiter.allow(client_ip)
                if not allowed:
                    app_logger.warning(f"429 Too Many Requests - {req.method} {req.url.path} from {client_ip}")
                    return JSONResponse(
                        status_code=429,
                        content={
                            "message": "Too Many Requests - rate limit exceeded",
                            "error_code": "rate_limited",
                            "limit_per_second": 100
                        },
                        headers={
                            "X-RateLimit-Limit": "100",
                            "X-RateLimit-Remaining": str(remaining),
                            "Retry-After": "1"
                        }
                    )
            response = await call_next(req)

        except Exception as exc:
            app_logger.exception(f"Unhandled exception for {req.method} {req.url.path} from {client_ip}")
            return JSONResponse(
                status_code=500,
                content={
                    "message": "An unexpected error occurred while processing the request.",
                    "error_code": "internal_server_error"
                }
            )

        # ---------- Request logging ----------
        duration = time.time() - start_time
        status_code = getattr(response, "status_code", "-")
        log_message = f"{req.method} {req.url.path} {status_code} from {client_ip} in {duration:.6f}s"

        if int(status_code) >= 500:
            app_logger.error(log_message)
        elif int(status_code) >= 400:
            app_logger.warning(log_message)
        else:
            app_logger.info(log_message)

        return response

    # ---------- Enable CORS ----------
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
