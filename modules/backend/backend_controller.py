import os
from typing import Optional
from uuid import uuid4

import aiofiles as aiofiles

from modules.accounts.account_control_service import AccountControlService
from modules.backend.config import temp_dir, public
from modules.names.names_service import NamesService
from modules.names.parsing_service import ParsingService
from modules.proxy.proxy_service import ProxyService
from modules.subscriptions.subscriptions_service import SubscriptionsService


class BackendController:
    def __init__(self, account_service: AccountControlService,
                 parsing_service: ParsingService,
                 names_service: NamesService,
                 subscriptions_service: SubscriptionsService,
                 proxy_service: ProxyService
                 ):
        self.account_service = account_service
        self.parsing_service = parsing_service
        self.names_service = names_service
        self.subscriptions_service = subscriptions_service
        self.proxy_service = proxy_service
        self.temp_dir = temp_dir
        self.public = public

    async def import_session(self, session_bytes: bytes, account_categories: [str] = None):
        path = self.temp_dir + f'\\{uuid4()}.session'
        async with aiofiles.open(path, 'wb') as out_file:
            await out_file.write(session_bytes)
        out = await self.account_service.import_user(path, account_categories)
        os.remove(path)
        return out

    async def get_image(self, user_id: int) -> bytes:
        user = await self.account_service.get_user(user_id)
        if user:
            if user.image:
                return open(user.image, 'rb').read()
        return open(self.public + "/0.png", 'rb').read()

    async def get_session(self, user_id: int) -> str:
        user = await self.account_service.get_user(user_id)
        if user:
            if user.image:
                return user.session

    async def get_accounts(self, active):
        if active:
            accounts = await self.account_service.get_accounts()
        else:
            accounts = await self.account_service.get_accounts(active=False)
        return [
            {
                'user_id': i.user_id,
                'first_name': i.first_name,
                'last_name': i.last_name,
                'phone': i.phone,
                'about': i.about,
                'username': i.username,
                'channel_join': i.channel_join,
                'categories': i.categories
            } | ({
                     "ban_time": i.inactive_date,
                     "ban_reason": i.inactive_reason,
                 } if not active else {})
            for i in accounts]

    async def change_account(self, account_id: int,
                             first_name: Optional[str] = None,
                             last_name: Optional[str] = None,
                             about: Optional[str] = None,
                             username: Optional[str] = None,
                             categories: Optional[list[str]] = None):
        await self.account_service.change_user_info(account_id, first_name, last_name, about, username, categories)

    async def update_account(self, account_id: int):
        await self.account_service.change_user(account_id)

    async def check_account(self, account_id: int):
        await self.account_service.check_user_id(account_id)

    async def get_active_accounts_ids(self):
        return [
            {
                'user_id': i.user_id
            }
            for i in (await self.account_service.get_accounts())]

    async def get_actual_parsing(self):
        parsings = await self.parsing_service.get_parsings()
        if len(parsings) == 0:
            return None
        return parsings[0]

    async def stop_parsing(self):
        parsings = await self.parsing_service.get_parsings()
        for i in parsings:
            await self.parsing_service.stop_parsing(i.id)

    async def start_parsing(self, link: str,
                            limit: Optional[int],
                            block: int,
                            delay_block: int,
                            delay_users: int,
                            user: int,
                            categories: list[str]):
        return await self.parsing_service.start_parsing(link, limit, block, delay_block, delay_users, user, categories)

    async def get_names_image(self, user_id: int) -> bytes:
        user = await self.names_service.get_name(user_id)
        if user:
            if user.image:
                return open(user.image, 'rb').read()
        return open(self.public + "/0.png", 'rb').read()

    async def get_names(self):
        return await self.names_service.get_names()

    async def edit_name(self, name_id: int, first_name: Optional[str], last_name: Optional[str], about: Optional[str],
                        username: Optional[str], categories: list[str]):
        return await self.names_service.edit_name(name_id, first_name, last_name, about, username, categories)

    async def delete_name(self, name_id: int):
        return await self.names_service.delete_name(name_id)

    async def get_subscriptions(self):
        return await self.subscriptions_service.get_subscriptions()

    async def create_subscription(self, link: str, timeline: list[(int, int, int)], categories: list[str], exclude_categories: list[str]):
        if categories == ['']:
            categories = None
        if exclude_categories == ['']:
            exclude_categories = None
        return await self.subscriptions_service.create_subscription(link, timeline, categories, exclude_categories)

    async def edit_subscription(self, subscription_id: int, status: str):
        await self.subscriptions_service.change_subscription_status(subscription_id, status)

    async def edit_subscription_count(self, subscription_id: int, timeline: (int, int, int)):
        await self.subscriptions_service.edit_subscription(subscription_id, timeline)

    async def get_proxies(self):
        return await self.proxy_service.get_proxies()

    async def add_proxies(self, proxy: str, categories: list[str]):
        return await self.proxy_service.add_proxies(proxy.removesuffix("\n").split("\n"))

    async def remove_proxy(self, proxy_id: int):
        return await self.proxy_service.remove_proxy(proxy_id)

    async def get_categories(self):
        return await self.account_service.get_categories()

    async def add_category(self, category: str):
        return await self.account_service.add_category(category)

    async def remove_category(self, category: str):
        return await self.account_service.remove_category(category)
