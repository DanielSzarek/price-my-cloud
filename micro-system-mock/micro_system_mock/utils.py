import asyncio

from .config import settings
import random
import aiohttp
import requests

range_from = settings.CPU_OPERATIONS.RANGE_FROM
range_to = settings.CPU_OPERATIONS.RANGE_TO
api_endpoints = settings.API_ENDPOINTS


def cpu_operations():
    rand = random.randint(range_from, range_to)
    for i in range(rand):
        _ = i * i


# async def make_request(session, endpoint):
#     try:
#         async with session.get(endpoint) as response:
#             print(f"Response from {endpoint}: {response.status}")
#     except aiohttp.ClientError as e:
#         print(f"Error connecting to {endpoint}: {e}")
#
#
# async def call_apis_async():
#     async with aiohttp.ClientSession() as session:
#         tasks = [make_request(session, endpoint) for endpoint in api_endpoints]
#         await asyncio.gather(*tasks)


async def call_api_async(api):
    async with aiohttp.ClientSession() as session:
        async with session.get(api) as response:
            data = await response.json()
            print(data)


async def call_apis_async():
    tasks = []
    for endpoint in api_endpoints.split(";"):
        tasks.append(asyncio.ensure_future(call_api_async(endpoint)))
    await asyncio.gather(*tasks)


def call_apis(counter):
    # By using counter we can set traffic once to endpoint A, once to endpoint B
    endpoints = api_endpoints.split(";")
    if counter % 2 == 0:
        response = requests.get(endpoints[0])
    else:
        response = requests.get(endpoints[-1])
    print(f"{response.status_code} - {response.json()}")
