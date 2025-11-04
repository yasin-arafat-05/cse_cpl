import logging
import sys
import os
import time 
from datetime import datetime
from typing import Annotated, List
from logging.handlers import TimedRotatingFileHandler
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from app.routes.current_user import get_current_admin_user
from app.db import model

# Ensure log directory exists
LOG_DIR = os.path.join("app","log")
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)


class DailyRotatingFileHandler(TimedRotatingFileHandler):
    def __init__(self, filename, backupCount: int = 0, encoding=None):
        super().__init__(filename, when='midnight', interval=1, backupCount=backupCount, encoding=encoding)


def _maybe_rollover_on_restart(log_file_path: str, threshold_seconds: int = 300) -> None:
    """
    If the current base log file exists and last modification is older than threshold,
    rename it with a timestamp suffix so that a fresh file is created after restart.
    This matches the requirement: after 5 minutes, on server restart, create a new log file.
    """
    try:
        if os.path.exists(log_file_path):
            mtime = os.path.getmtime(log_file_path)
            if (time.time() - mtime) >= threshold_seconds:
                timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                rotated_name = f"{log_file_path}.{timestamp}"
                os.rename(log_file_path, rotated_name)
    except Exception as e:
        # Fall back silently to continue logging even if rename fails
        print(f"Log rollover on restart check failed: {e}")


def setup_logger():
    logger = logging.getLogger("my_fastapi_app")
    logger.setLevel(logging.DEBUG)

    # Avoid adding duplicate handlers on hot-reload
    if logger.handlers:
        return logger

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(console_format)
    logger.addHandler(console_handler)

    # Base log file
    log_file_path = os.path.join(LOG_DIR, "app.log")

    # If the existing base log is older than 5 minutes and process restarted, rotate it now
    _maybe_rollover_on_restart(log_file_path, threshold_seconds=300)

    # Ensure the base file exists at startup
    if not os.path.exists(log_file_path):
        open(log_file_path, 'a').close()

    # Daily rotation at midnight
    file_handler = DailyRotatingFileHandler(log_file_path, backupCount=0)
    file_handler.setLevel(logging.DEBUG)
    file_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(pathname)s:%(lineno)d - %(message)s')
    file_handler.setFormatter(file_format)
    logger.addHandler(file_handler)

    logger.info("Logger initialized. Daily rotation at midnight enabled.")
    return logger


# ================= Admin Log Management Endpoints =================
router = APIRouter(tags=['Admin Logs'])


def _list_log_files() -> List[dict]:
    files = []
    try:
        for name in os.listdir(LOG_DIR):
            path = os.path.join(LOG_DIR, name)
            if os.path.isfile(path):
                stat = os.stat(path)
                files.append({
                    "filename": name,
                    "size_bytes": stat.st_size,
                    "modified": datetime.fromtimestamp(stat.st_mtime).isoformat()
                })
        files.sort(key=lambda x: x["modified"], reverse=True)
    except FileNotFoundError:
        pass
    return files


@router.get("/logs", summary="List log files")
async def list_logs(current_admin: Annotated[model.Player, Depends(get_current_admin_user)]):
    return {"files": _list_log_files()}


@router.get("/logs/{filename}/download", summary="Download a log file")
async def download_log_file(filename: str, current_admin: Annotated[model.Player, Depends(get_current_admin_user)]):
    path = os.path.join("app","log",f"{filename}")
    if not os.path.exists(path) or not os.path.isfile(path):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found")
    return FileResponse(path, media_type="text/plain", filename=filename)


@router.delete("/logs/{filename}", status_code=204, summary="Delete a log file")
async def delete_log_file(filename: str, current_admin: Annotated[model.Player, Depends(get_current_admin_user)]):
    if filename == "app.log":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot delete active log file 'app.log'")
    path = path = os.path.join("app","log",f"{filename}")
    if not os.path.exists(path) or not os.path.isfile(path):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found")
    try:
        os.remove(path)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to delete file: {e}")
    return

