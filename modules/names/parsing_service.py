import asyncio
from asyncio import Task
from typing import Optional

from modules.accounts.account_control_service import AccountControlService
from modules.names.entity.parsing import Parsing
from modules.names.names_service import NamesService
from modules.names.parsing_repository import ParsingRepository
from modules.names.parsing_telethon import ParsingTelethon
from modules.names.parsing_worker import ParsingWorker
from modules.proxy.proxy_service import ProxyService

tasks: {int, Task} = {}


class ParsingService:
    def __init__(self, parsing_repository: ParsingRepository, names_service: NamesService,
                 account_service: AccountControlService, proxy_service: ProxyService):
        self.parsing_repository = parsing_repository
        self.names_service = names_service
        self.account_service = account_service
        self.proxy_service = proxy_service

    async def get_parsings(self):
        return await self.parsing_repository.get_parsings()

    async def start_parsing(self, link: str, limit: Optional[int], block: int, time_delay: int, time_delay_user: int,
                            user_id: int, categories: list[str]):
        if len(await self.get_parsings()) != 0:
            return
        parsing = Parsing(link=link.removeprefix("https://").removeprefix("t.me/"), account_id=user_id, limit=limit, block=block, time_delay_get_user=time_delay_user,
                          time_delay=time_delay, categories=categories)
        parsing = await self.parsing_repository.save_parsing(parsing)
        account = await self.account_service.get_user(user_id)
        if not account:
            return
        parsing_telethon = ParsingTelethon(account.session, self.proxy_service)
        parsing_worker = ParsingWorker(parsing, self.parsing_repository, self.names_service, parsing_telethon)
        task = asyncio.create_task(parsing_worker.run())
        tasks.update({parsing.id: task})
        return parsing

    async def get_parsing(self, parsing_id: int):
        return await self.parsing_repository.get_parsing(parsing_id)

    async def stop_parsing(self, parsing_id: int):
        if parsing_id in tasks:
            tasks.get(parsing_id).cancel()
            tasks.pop(parsing_id)
        return await self.parsing_repository.delete_parsing(parsing_id)
