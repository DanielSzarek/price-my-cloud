import asyncio

from .config import settings
import random
import aiohttp

range_from = settings.CPU_OPERATIONS.RANGE_FROM
range_to = settings.CPU_OPERATIONS.RANGE_TO
api_endpoints = settings.API_ENDPOINTS


def cpu_operations():
    rand = random.randint(range_from, range_to)
    for i in range(rand):
        _ = i * i


async def make_request(session, endpoint):
    try:
        async with session.get(endpoint) as response:
            print(f"Response from {endpoint}: {response.status}")
    except aiohttp.ClientError as e:
        print(f"Error connecting to {endpoint}: {e}")


async def call_apis():
    async with aiohttp.ClientSession() as session:
        tasks = [make_request(session, endpoint) for endpoint in api_endpoints]
        await asyncio.gather(*tasks)
