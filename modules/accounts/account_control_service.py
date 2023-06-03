import random
import time
from typing import Optional

from modules.accounts.account_category_repository import AccountCategoryRepository
from modules.accounts.account_telethon import AccountTelethon
from modules.accounts.accounts_repository import AccountsRepository
from modules.accounts.entity.account import AccountStatus, Account, AccountCategory
from modules.accounts.exceptions import AccountBannedException
from modules.names.names_service import NamesService
from modules.proxy.proxy_service import ProxyService


class AccountControlService:
    def __init__(self,
                 accounts_repository: AccountsRepository,
                 account_category_repository: AccountCategoryRepository,
                 names_service: NamesService,
                 proxy_service: ProxyService
                 ):
        self.accounts_repository = accounts_repository
        self.account_category_repository = account_category_repository
        self.names_service = names_service
        self.proxy_service = proxy_service

    async def get_categories(self):
        return await self.account_category_repository.get_categories()

    async def add_category(self, category):
        return await self.account_category_repository.add_category(category)

    async def remove_category(self, category):
        return await self.account_category_repository.remove_category(category)

    async def get_accounts(self, categories: Optional[list[AccountCategory | str]] = None,
                           active=True) -> list[Account]:
        accounts = await self.accounts_repository.get_accounts()
        if active:
            accounts = list(filter(lambda a: a.status == AccountStatus.active, accounts))
        else:
            accounts = list(filter(lambda a: a.status == AccountStatus.inactive, accounts))

        if categories:
            if len(categories) >= 0 and categories != ['']:
                accounts = list(filter(lambda i: any([j in categories for j in i.categories]), accounts))
        return accounts

    async def get_user(self, user_id: int) -> Account:
        account = await self.accounts_repository.get_account(user_id)
        return account

    async def user_fail(self, user_id: int, reason: str = ''):
        account = await self.accounts_repository.get_account(user_id)
        account.status = AccountStatus.inactive
        account.inactive_reason = reason
        account.inactive_date = int(time.time())
        await self.accounts_repository.save_account(account)

    async def import_user(self, session: str, categories: [AccountCategory] = []):
        """ if user already in base don't change name """
        try:
            account = await self.check_user(session)
            account.categories += categories
            pre_account = await self.accounts_repository.get_account(account.user_id)
            if pre_account:
                account.categories += pre_account.categories
                await self.accounts_repository.save_account(account)
            else:
                await self.accounts_repository.save_account(account)
                await self.change_user(account.user_id, categories)
        except AccountBannedException:
            return False
        return True

    async def check_user(self, session: str) -> Account:
        account = Account(session=session)
        account_telethon = AccountTelethon(account.session, self.proxy_service, account.categories)
        info = await account_telethon.get_account_information()
        account.user_id = info['user_id']
        account.phone = info['phone']
        account.first_name = info['first_name']
        account.last_name = info['last_name']
        account.username = info['username']
        account.status = AccountStatus.active
        if random.random() <= 0.75:
            await account_telethon.hide_active_time()
        await account_telethon.close()
        return account

    async def change_user_teg(self, account_id: int,
                              add_categories: Optional[list[str]] = None,
                              remove_categories: Optional[list[str]] = None):
        account = await self.accounts_repository.get_account(account_id)
        if not account:
            return
        if add_categories:
            for i in add_categories:
                account.categories.append(i)

        if remove_categories:
            for i in remove_categories:
                account.categories.remove(i)

        await self.accounts_repository.save_account(account)

    async def change_user_info(self, account_id: int,
                               first_name: Optional[str] = None,
                               last_name: Optional[str] = None,
                               about: Optional[str] = None,
                               username: Optional[str] = None,
                               categories: Optional[list[str]] = None):
        account = await self.accounts_repository.get_account(account_id)
        if not account:
            return
        if first_name or first_name == '':
            account.first_name = first_name
        if last_name or last_name == '':
            account.last_name = last_name
        if about or about == '':
            account.about = about
        if username:
            account.username = username
        if categories is not None:
            account.categories = categories

        try:
            account_telethon = AccountTelethon(account.session, self.proxy_service, account.categories)
            if first_name or last_name or about or username:
                print('edit')
                await account_telethon.edit_profile(first_name, last_name, about, username, None)
                await account_telethon.close()
            await self.accounts_repository.save_account(account)
            return True
        except AccountBannedException as e:
            await self.user_fail(account.user_id, e.reason)
            return False

    async def check_user_id(self, user_id: int):
        account = await self.accounts_repository.get_account(user_id)
        if account:
            try:
                account_telethon = AccountTelethon(account.session, self.proxy_service, account.categories)
                info = await account_telethon.get_account_information()
                account.user_id = info['user_id']
                account.phone = info['phone']
                account.first_name = info['first_name']
                account.last_name = info['last_name']
                account.username = info['username']
                account.status = AccountStatus.active
                await account_telethon.close()
                await self.accounts_repository.save_account(account)
            except AccountBannedException as e:
                await self.user_fail(user_id, e.reason)
                return False

    async def change_user(self, user_id: int, categories: [AccountCategory] = []) -> bool:
        account = await self.accounts_repository.get_account(user_id)
        name = await self.names_service.pop_random_name()
        if not name:
            account.categories.append(AccountCategory.not_changed)
            account.categories += categories
            await self.accounts_repository.save_account(account)
            return False
        try:
            account_telethon = AccountTelethon(account.session, self.proxy_service, account.categories)
            if not name.last_name:
                name.last_name = ''
            if not name.about:
                name.about = ''
            await account_telethon.edit_profile(name.first_name, name.last_name, name.about,
                                                name.new_username, name.image)
            await account_telethon.close()
            if type(name.image) == str:
                account.image = name.image
            account.first_name = name.first_name
            account.last_name = name.last_name
            account.about = name.about
            account.username = name.new_username
            account.categories = name.categories + categories
            await self.accounts_repository.save_account(account)
            await self.names_service.delete_name(name.id)
            return True
        except AccountBannedException as e:
            await self.user_fail(user_id, e.reason)
            return False

    async def subscribe_channel_by_link(self, user_id: int, link: str) -> int:
        """-1 - banned, 0 - success, 1 - already"""
        account = await self.accounts_repository.get_account(user_id)
        if not account:
            return False
        try:
            account_t = AccountTelethon(account.session, self.proxy_service, account.categories)
            out = await account_t.subscribe_channel_by_link(link)
            account.channel_join += 1
            await self.accounts_repository.save_account(account)
            await account_t.close()
            return out
        except AccountBannedException as e:
            await self.user_fail(user_id, e.reason)
            return -1
