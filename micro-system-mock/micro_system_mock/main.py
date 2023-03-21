import asyncio
from time import time

from fastapi import FastAPI

from . import utils
from .config import settings
from .db import get_logs, create_log, LogCreate

app = FastAPI()


@app.get("/")
def read_root():
    start = time()
    if settings.SHOULD_PERFORM_CPU_OPERATIONS:
        utils.cpu_operations()

    if settings.SHOULD_CALL_DB:
        print("Calling DB")
        log = LogCreate(log_data="Log message")
        create_log(log)
        print(f"DB log Count: {len(get_logs())}")

    if settings.SHOULD_CALL_APIS:
        print("Calling API")
        utils.call_apis()

    duration = time() - start

    return {
        "status": "OK",
        "operations_duration": duration,
    }
