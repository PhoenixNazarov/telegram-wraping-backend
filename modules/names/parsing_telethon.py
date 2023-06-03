import asyncio

from telethon.tl.functions.channels import GetParticipantsRequest
from telethon.tl.functions.users import GetFullUserRequest
from telethon.tl.types import ChannelParticipantsSearch

from modules.accounts.account_telethon import AccountTelethon
from modules.names.names_service import NamesService


class ParsingTelethon(AccountTelethon):
    async def parse_chat(self, link: str, offset: int, block: int, image_out: str, delay: int, categories: list[str],
                         names_service: NamesService):
        client = await self.get_client()
        participants = await client(
            GetParticipantsRequest(channel=link,
                                   filter=ChannelParticipantsSearch(''),
                                   offset=offset,
                                   limit=block,
                                   hash=0)
        )
        for i in participants.users:
            if i.bot:
                continue
            photo = None
            image_path = None
            if i.photo:
                image_path = image_out + f"/{i.id}.jpg"
                await client.download_profile_photo(i.id, file=image_path)
                photo = open(image_path, 'rb').read()
            full = await client(GetFullUserRequest(i))
            await names_service.add_name(i.id, i.first_name, i.last_name, full.full_user.about, i.username, image_path,
                                         categories)
            await asyncio.sleep(delay)
        await self.close()
