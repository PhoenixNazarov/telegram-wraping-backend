from abc import ABC, abstractmethod
from typing import Optional

from modules.subscriptions.entity.subscription import Subscription


class SubscriptionRepository(ABC):
    @abstractmethod
    async def save_subscription(self, subscription: Subscription) -> Subscription:
        pass

    @abstractmethod
    async def get_subscriptions(self) -> list[Subscription]:
        pass

    @abstractmethod
    async def get_subscription(self, subscription_id: int) -> Optional[Subscription]:
        pass

    @abstractmethod
    async def change_unit_status(self, subscription_id: int, unit_id: int, account_id: Optional[int], status: str):
        pass

    @abstractmethod
    async def add_unit(self, subscription_id: int, account_id: int, status: str):
        pass

    @abstractmethod
    async def change_current_time(self, subscription_id: int, current_time: int):
        pass

    @abstractmethod
    async def change_status(self, subscription_id: int, status: str):
        pass
