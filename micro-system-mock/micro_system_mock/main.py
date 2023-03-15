import random

from fastapi import FastAPI
from time import time
from .config import settings

app = FastAPI()


@app.get("/")
def read_root():
    rand = random.randint(settings.range_from, settings.range_to)
    start = time()
    for i in range(rand):
        _ = i * i
    duration = time() - start

    return {
        "status": "OK",
        "operations_duration": duration,
    }
