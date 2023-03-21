import asyncio
import time
from os import getenv
import aiohttp
import requests

endpoints_to_call = getenv("API_ENDPOINTS", "").split(";")
sleep_time = int(getenv("SLEEP_TIME", 1))


async def make_request(endpoint, session):
    try:
        async with session.get(endpoint) as response:
            print(f"Response from {endpoint}: {response.status_code}")
    except aiohttp.ClientError as e:
        print(f"Error connecting to {endpoint}: {e}")


async def call_apis():
    async with aiohttp.ClientSession() as session:
        tasks = [make_request(endpoint, session) for endpoint in endpoints_to_call]
        print(f"Tasks: {tasks}")
        await asyncio.gather(*tasks)


if __name__ == "__main__":
    while True:
        # call_apis()
        for endpoint in endpoints_to_call:
            response = requests.get(endpoint)
            print(f"Response from {endpoint}: {response.status_code}")
            print(response.json())
        time.sleep(sleep_time)
