from modules.accounts.account_control_service import AccountControlService
from modules.accounts.entity.account import Account
from modules.messages.message_telethon import MessageTelethon
from modules.proxy.proxy_service import ProxyService


class MessageService:
    def __init__(self, account_service: AccountControlService, proxy_servie: ProxyService):
        self.account_service = account_service
        self.proxy_service = proxy_servie

    async def get_users(self):
        return await self.account_service.get_accounts()

    async def read_message(self, account: Account):
        account = MessageTelethon(account.session, self.proxy_service, account.account_device,
                                  account.categories)

        try:
            await account.read_all_message()
        except Exception as e:
            print(e)
