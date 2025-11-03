
import time
import logging
from fastapi import FastAPI
from fastapi import Request
from fastapi.middleware.cors import CORSMiddleware

# desiable fast api resonses:
logger = logging.getLogger("uvicorn.access")
logger.disabled = True 


def register_middleware(app:FastAPI):
    @app.middleware("http")
    async def custom_loggin(req:Request,call_next):
        brefore_calling = time.time()
        try:
            response = await call_next(req)
        except Exception as exc:
            from fastapi.responses import JSONResponse
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
            log_messages = f"{req.method} - {req.url.path} - status_code: {status_code} - completed after: {diff:6f} seccond"
            print(log_messages)
        return response
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    