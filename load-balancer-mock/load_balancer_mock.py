import asyncio
import time
from os import getenv
import aiohttp
import requests

endpoints_to_call = getenv("API_ENDPOINTS", "").split(";")
sleep_time = int(getenv("SLEEP_TIME", 1))


async def call_api_async(api, counter):
    async with aiohttp.ClientSession() as session:
        async with session.get(api, params={"counter": counter}) as response:
            data = await response.json()
            print(data)


async def call_apis_async():
    tasks = []
    for endpoint in endpoints_to_call:
        for i in range(10):
            tasks.append(asyncio.ensure_future(call_api_async(endpoint, i)))
    await asyncio.gather(*tasks)


if __name__ == "__main__":
    start = time.time()
    for _ in range(30):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(call_apis_async())
    # time.sleep(sleep_time)
    print(f"Processing time: {time.time() - start}")
