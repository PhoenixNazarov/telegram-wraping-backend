from modules.accounts.entity.account import Account
from modules.messages.massage_service import MessageService
import asyncio


class MessageReader:
    def __init__(self, message_service: MessageService):
        self.message_service = message_service

    async def read_message(self, account: Account):
        await self.message_service.read_message(account)

    async def run(self):
        while True:
            accounts = await self.message_service.get_users()

            for a in accounts:
                asyncio.create_task(self.read_message(a))
                await asyncio.sleep(60 * 60 / len(accounts))
