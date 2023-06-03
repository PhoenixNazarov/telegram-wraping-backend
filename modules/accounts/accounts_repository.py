from abc import ABC, abstractmethod
from typing import Optional

from modules.accounts.entity.account import Account


class AccountsRepository(ABC):
    @abstractmethod
    async def get_account(self, user_id: int) -> Optional[Account]:
        pass

    @abstractmethod
    async def get_accounts(self) -> list[Account]:
        pass

    @abstractmethod
    async def update_image(self, account: Account, image: str):
        pass

    @abstractmethod
    async def save_account(self, account: Account) -> Account:
        pass
