import asyncio

from modules.proxy.proxy_checker import ProxyChecker
from modules.utils.service_factories import create_proxy_repository


async def main():
    tasks = []
    tasks.append(
        asyncio.create_task(ProxyChecker(create_proxy_repository()).run())
    )
    for t in tasks:
        await t


asyncio.run(main())
