import json
import os.path
import shutil
from pathlib import Path
from typing import Optional

from modules.accounts.accounts_repository import AccountsRepository
from modules.accounts.entity.account import Account


def create_dir_if_not_exist(path):
    if not os.path.exists(path):
        os.mkdir(path)


def write_if_not_exist(path, string):
    if not os.path.exists(path):
        with open(path, 'w') as file:
            file.write(string)


class AccountsRepositoryImpl(AccountsRepository):
    def __init__(self, path):
        self.path = Path(path)
        self.sessions_path = Path(path) / "sessions"
        self.images_path = Path(path) / "images"
        self.account_information = Path(path) / "info.json"

        create_dir_if_not_exist(self.path)
        create_dir_if_not_exist(self.sessions_path)
        create_dir_if_not_exist(self.images_path)
        write_if_not_exist(self.account_information, '{}')

    def get_base(self):
        with open(self.account_information, 'r') as file:
            return json.loads(file.read())

    def save_base(self, data):
        with open(self.account_information, 'w') as file:
            file.write(json.dumps(data))

    def get_session_path(self, user_id: int) -> Optional[str]:
        return str(self.sessions_path / f'{user_id}.session')

    def get_image_path(self, user_id: int) -> Optional[str]:
        return str(self.images_path / f'{user_id}.png')

    async def get_account(self, user_id: int) -> Optional[Account]:
        base = self.get_base()
        if str(user_id) not in base:
            return None
        account = Account.parse_raw(base[str(user_id)])
        account.session = self.get_session_path(account.user_id)
        if os.path.exists(self.get_image_path(account.user_id)):
            account.image = self.get_image_path(account.user_id)
        else:
            account.image = None
        return account

    async def get_accounts(self) -> list[Account]:
        base = self.get_base()
        out = []
        for i in base.values():
            account = Account.parse_raw(i)
            account.session = self.get_session_path(account.user_id)
            if os.path.exists(self.get_image_path(account.user_id)):
                account.image = self.get_image_path(account.user_id)
            else:
                account.image = None
            out.append(account)
        return out

    async def update_image(self, account: Account, image: str) -> Account:
        image_path = self.get_image_path(account.user_id)
        shutil.copy(account.image, image_path)
        account.image = image_path
        return account

    async def save_account(self, account: Account) -> Account:
        base = self.get_base()

        session_path = self.get_session_path(account.user_id)
        if account.session != session_path:
            shutil.copy(account.session, session_path)
            account.session = session_path
        image_path = self.get_image_path(account.user_id)
        if account.image and account.image != image_path:
            shutil.copy(account.image, image_path)
            account.image = image_path

        base[str(account.user_id)] = account.json()
        self.save_base(base)
        return account
