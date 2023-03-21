import asyncio
import logging
from time import time

from fastapi import FastAPI

from . import utils
from .config import settings
from .db import get_logs, create_log, LogCreate

app = FastAPI()
logger = logging.getLogger("uvicorn")


@app.get("/")
def read_root():
    start = time()
    if settings.SHOULD_PERFORM_CPU_OPERATIONS:
        utils.cpu_operations()

    if settings.SHOULD_CALL_APIS:
        logger.info("Calling API")
        utils.call_apis()

    if settings.SHOULD_CALL_DB:
        logger.info("Calling DB")
        try:
            log = LogCreate(log_data="Log message")
            create_log(log)
            logs = get_logs()
            logger.info(f"DB log Count: {len(logs)}")
        except Exception as e:
            logger.error(str(e))

    duration = time() - start

    return {
        "status": "OK",
        "operations_duration": duration,
    }
