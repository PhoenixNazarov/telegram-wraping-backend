import asyncio
import os.path
import random
from typing import Optional

from telethon import TelegramClient
from telethon.errors import SessionRevokedError, UsernameOccupiedError, AuthKeyUnregisteredError, \
    UserAlreadyParticipantError, UserDeactivatedBanError, UsernameInvalidError, AboutTooLongError, \
    InviteRequestSentError, ChannelsTooMuchError, UserDeactivatedError
from telethon.tl.functions.account import UpdateProfileRequest, UpdateUsernameRequest, UpdateStatusRequest, \
    SetPrivacyRequest
from telethon.tl.functions.channels import JoinChannelRequest
from telethon.tl.functions.messages import ImportChatInviteRequest
from telethon.tl.functions.photos import UploadProfilePhotoRequest, DeletePhotosRequest
from telethon.tl.types import InputPhoto, InputPrivacyKeyStatusTimestamp, InputPrivacyValueAllowContacts

from modules.accounts.entity.account import AccountDeviceData
from modules.accounts.exceptions import AccountBannedException
from modules.proxy.proxy_service import ProxyService

clients = {}


class AccountTelethon:
    def __init__(self, session_path: str, proxy_service: ProxyService, account_device: AccountDeviceData, categories: list[str] = []):
        self.session_path = session_path.removesuffix('.session')
        self.client = None
        self.proxy_service = proxy_service
        self.categories = categories
        self.account_device = account_device

    async def get_client(self) -> TelegramClient:
        if not self.client:
            if self.session_path in clients:
                self.client = clients[self.session_path]
            else:
                count = 0
                while 1:
                    try:
                        proxy = await self.proxy_service.get_random_proxy(self.categories)
                        self.client = TelegramClient(
                            self.session_path,
                            api_id=self.account_device.api_id,
                            api_hash=self.account_device.api_hash,
                            device_model=self.account_device.device_model,
                            system_version=self.account_device.system_version,
                            app_version=self.account_device.app_version,
                            lang_code=self.account_device.lang_code,
                            system_lang_code=self.account_device.lang_code,
                            proxy=proxy,
                            timeout=8
                        )
                        await self.client.connect()
                        clients[self.session_path] = self.client
                        break
                    except ConnectionError:
                        count += 1
                        pass
        return self.client

    async def set_online(self, timeout=10):
        await self.get_client()
        await self._do(self.client(UpdateStatusRequest(offline=False)))
        asyncio.create_task(self._set_offline(random.randint(3, 300)))

    async def _set_offline(self, timeout=10):
        await asyncio.sleep(timeout)
        client = await self.get_client()
        await self._do(client(UpdateStatusRequest(offline=True)))
        await self.close()

    async def hide_active_time(self):
        await self.get_client()
        await self.client(SetPrivacyRequest(
            key=InputPrivacyKeyStatusTimestamp(),
            rules=[InputPrivacyValueAllowContacts()]
        ))

    async def _do(self, coro):
        count = 0
        while 1:
            if count >= 10:
                await self.close()
                return -1
            try:
                return await coro
            except ConnectionError:
                count += 1
                await self.close()
                await self.get_client()
            # BANNED
            except UserDeactivatedBanError:
                await self.close()
                raise AccountBannedException('UserDeactivatedBanError')
            except AuthKeyUnregisteredError:
                await self.close()
                raise AccountBannedException('AuthKeyUnregisteredError')
            except SessionRevokedError:
                await self.close()
                raise AccountBannedException('SessionRevokedError')
            except UserDeactivatedError:
                return
            except Exception as e:
                print(e)
                raise e

    async def get_account_information(self) -> {str, int | str}:
        """user_id, phone, first_name, last_name, username"""
        client = await self.get_client()
        me = await self._do(client.get_me())
        await self.set_online()
        if not me:
            raise AccountBannedException('Not me')

        return {
            'user_id': me.id,
            'phone': me.phone,
            'first_name': me.first_name,
            'last_name': me.last_name,
            'username': me.username
        }

    async def check_connect(self):
        await self.get_client()
        await self.set_online()
        return True

    async def close(self):
        if self.client is None:
            return
        client = await self.get_client()
        self.client = None
        clients.pop(self.session_path)
        await client.disconnect()

    async def subscribe_channel_by_link(self, link: str, join_link: bool = True) -> int:
        client = await self.get_client()
        try:
            await self.set_online()

            if join_link:
                link = link.removeprefix("https://").removeprefix("t.me/").removeprefix("+")
                out = await self._do(
                    client(ImportChatInviteRequest(link)))
            else:
                channel = self._do(await self.client.get_entity(link))
                out = await self._do(self.client(JoinChannelRequest(channel)))
            if out == -1:
                return 1
            else:
                return 0
        except UserAlreadyParticipantError:
            return 1
        except InviteRequestSentError:
            return 0
        except ChannelsTooMuchError:
            raise AccountBannedException("ChannelsTooMuchError")

    async def edit_profile(self,
                           first_name: Optional[str],
                           last_name: Optional[str],
                           about: Optional[str],
                           username: Optional[str],
                           photo: Optional[str]):
        await self.set_online()
        client = await self.get_client()
        if first_name or last_name or about:
            try:
                await self._do(client(UpdateProfileRequest(first_name=first_name, last_name=last_name, about=about)))
            except UsernameInvalidError:
                pass
            except AboutTooLongError:
                pass
        if username and username != '':
            try:
                await self._do(client(UpdateUsernameRequest(username)))
            except UsernameOccupiedError:
                pass

        if photo:
            if os.path.exists(photo):
                ps = await self._do(client.get_profile_photos('me'))
                await self._do(client(DeletePhotosRequest(
                    id=[InputPhoto(
                        id=p.id,
                        access_hash=p.access_hash,
                        file_reference=p.file_reference
                    ) for p in ps])
                ))
                await self._do(client(UploadProfilePhotoRequest(file=await client.upload_file(photo))))
