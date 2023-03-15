from os import getenv

from pydantic import BaseSettings


class Settings(BaseSettings):
    range_from = getenv("RANGE_FROM", 1_000_000)
    range_to = getenv("RANGE_TO", 25_000_000)


settings = Settings()
