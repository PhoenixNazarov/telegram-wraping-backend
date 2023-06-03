import asyncio

from modules.names.entity.parsing import Parsing
from modules.names.names_service import NamesService
from modules.names.parsing_repository import ParsingRepository
from modules.names.parsing_telethon import ParsingTelethon


class ParsingWorker:
    def __init__(self, parsing: Parsing, parsing_repository: ParsingRepository, names_service: NamesService,
                 parsing_telethon: ParsingTelethon):
        self.parsing = parsing
        self.parsing_repository = parsing_repository
        self.names_service = names_service
        self.parsing_telethon = parsing_telethon

    async def update_parsing(self, parsing_id: int, current_offset: int):
        parsing = await self.parsing_repository.get_parsing(parsing_id)
        if parsing:
            parsing.current_offset = current_offset
            await self.parsing_repository.save_parsing(parsing)

    async def run(self):
        while True:
            self.parsing = await self.parsing_repository.get_parsing(self.parsing.id)
            if not self.parsing:
                return

            if self.parsing.limit:
                if self.parsing.current_offset >= self.parsing.limit:
                    await self.parsing_repository.delete_parsing(self.parsing.id)
                    return
            try:
                await self.parsing_telethon.parse_chat(self.parsing.link,
                                                       self.parsing.current_offset,
                                                       self.parsing.block,
                                                       self.parsing.image_dir,
                                                       self.parsing.time_delay_get_user,
                                                       self.parsing.categories,
                                                       self.names_service)
            except:
                await self.parsing_repository.delete_parsing(self.parsing.id)
                return

            await self.update_parsing(self.parsing.id, self.parsing.current_offset + self.parsing.block)
            await asyncio.sleep(self.parsing.time_delay)
