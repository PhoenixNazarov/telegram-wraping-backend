import asyncio

from modules.accounts.account_telethon import AccountTelethon


class MessageTelethon(AccountTelethon):
    async def read_all_message(self):
        client = await self.get_client()
        dialogs = await self._do(client.get_dialogs())
        count = 0
        for dialog in dialogs:
            if dialog.is_user:
                await self._do(client.send_read_acknowledge(dialog.entity, ))
                count += 1
                if count >= 5:
                    break

                await asyncio.sleep(1)
        await self.close()
