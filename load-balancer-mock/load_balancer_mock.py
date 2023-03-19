import asyncio
import time
from os import getenv
import aiohttp

endpoints_to_call = getenv("ENDPOINTS_TO_CALL", "").split(";")
sleep_time = getenv("SLEEP_TIME", 1)


async def make_request(endpoint, session):
    try:
        async with session.get(endpoint) as response:
            print(f"Response from {endpoint}: {response.status}")
    except aiohttp.ClientError as e:
        print(f"Error connecting to {endpoint}: {e}")


async def call_apis():
    async with aiohttp.ClientSession() as session:
        tasks = [make_request(endpoint, session) for endpoint in endpoints_to_call]
        await asyncio.gather(*tasks)


if __name__ == "__main__":
    while True:
        call_apis()
        time.sleep(sleep_time)
