import asyncio

from modules.messages.message_reader import MessageReader
from modules.utils.service_factories import create_messages_service


async def main():
    tasks = []
    tasks.append(
        asyncio.create_task(MessageReader(create_messages_service()).run())
    )
    for t in tasks:
        await t


asyncio.run(main())
