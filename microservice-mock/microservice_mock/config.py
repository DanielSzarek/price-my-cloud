from os import getenv
from types import SimpleNamespace

from pydantic import BaseSettings


class Settings(BaseSettings):
    SHOULD_PERFORM_CPU_OPERATIONS = getenv("SHOULD_PERFORM_CPU_OPERATIONS", True)
    CPU_OPERATIONS = SimpleNamespace(
        RANGE_FROM=int(getenv("RANGE_FROM", 500_000)),
        RANGE_TO=int(getenv("RANGE_TO", 10_000_000)),
    )
    SHOULD_CALL_DB = bool(getenv("SHOULD_CALL_DB", False))
    DB_CONNECTION_STRING = getenv(
        "DB_CONNECTION_STRING", "postgresql://postgres:postgres@localhost/postgres"
    )
    SHOULD_CALL_APIS = bool(getenv("SHOULD_CALL_APIS", False))
    API_ENDPOINTS = getenv("API_ENDPOINTS", "")


settings = Settings()
