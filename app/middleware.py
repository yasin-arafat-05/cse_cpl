import time
import logging
import asyncio
from typing import Dict, Tuple
from fastapi import FastAPI
from fastapi import Request
from fastapi.middleware.cors import CORSMiddleware

# desiable fast api resonses:
logger = logging.getLogger("uvicorn.access")
logger.disabled = True 
app_logger = logging.getLogger("my_fastapi_app")


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


def register_middleware(app:FastAPI):
    rate_limiter = FixedWindowRateLimiter(max_requests=100, window_seconds=1.0)

    @app.middleware("http")
    async def custom_loggin(req:Request,call_next):
        brefore_calling = time.time()
        client_ip = getattr(req.client, "host", "unknown")
        allowlisted_paths = {"/", "/health", "/docs", "/openapi.json"}
        if req.url.path not in allowlisted_paths:
            allowed, remaining = await rate_limiter.allow(client_ip)
            if not allowed:
                from fastapi.responses import JSONResponse
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
        try:
            response = await call_next(req)
        except Exception as exc:
            from fastapi.responses import JSONResponse
            app_logger.exception(f"Unhandled exception for {req.method} {req.url.path} from {client_ip}")
            response = JSONResponse(
                status_code=500,
                content={
                    "message": "An unexpected error occurred while processing the request.",
                    "error_code": "internal_server_error"
                }
            )
        finally:
            after_calling = time.time()
            diff = after_calling-brefore_calling
            try:
                status_code = getattr(response, "status_code", "-")
            except Exception:
                status_code = "-"
            log_messages = f"{req.method} {req.url.path} {status_code} from {client_ip} in {diff:6f}s"
            try:
                code_int = int(status_code)
            except Exception:
                code_int = 0
            if code_int >= 500:
                app_logger.error(log_messages)
            elif code_int >= 400:
                app_logger.warning(log_messages)
            else:
                app_logger.info(log_messages)
        return response
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    