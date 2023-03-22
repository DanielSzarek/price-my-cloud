import asyncio
import logging
from time import time

from fastapi import FastAPI

from . import utils
from .config import settings
from .db import get_logs, create_log, LogCreate

app = FastAPI()
logger = logging.getLogger(__name__)
counter = -1


@app.get("/")
def read_root():
    global counter
    counter += 1

    start = time()
    logger.error("Start")
    if settings.SHOULD_PERFORM_CPU_OPERATIONS:
        utils.cpu_operations()

    if settings.SHOULD_CALL_APIS:
        logger.error("Calling API")
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(utils.call_apis_async(counter))
        # logger.error(f"Counter: {counter}")

    if settings.SHOULD_CALL_DB:
        logger.error("Calling DB")
        try:
            log = LogCreate(log_data="Log message")
            create_log(log)
            logs = get_logs()
            logger.error(f"DB log Count: {len(logs)}")
        except Exception as e:
            logger.error(str(e))

    duration = time() - start

    return {
        "status": "OK",
        "operations_duration": duration,
    }
