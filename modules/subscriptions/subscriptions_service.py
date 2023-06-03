import asyncio
import random

from modules.accounts.account_control_service import AccountControlService
from modules.subscriptions.entity.subscription import Subscription, SubscriptionUnit, SubscriptionStatus
from modules.subscriptions.subscription_worker import SubscriptionWorker
from modules.subscriptions.subscriptions_repository import SubscriptionRepository

tasks = {}


class SubscriptionsService:
    def __init__(self, account_service: AccountControlService, subscription_repository: SubscriptionRepository):
        self.account_service = account_service
        self.subscription_repository = subscription_repository

    async def create_subscription(self, link: str, timeline: list[(int, int, int)], categories: list[str]):
        subscription = Subscription(link=link, categories=categories)
        for i in timeline:
            for j in range(i[2]):
                unit = SubscriptionUnit(time_delay=random.randint(i[0], i[1]))
                subscription.timeline.append(unit)
        return await self.subscription_repository.save_subscription(subscription)

    async def get_subscriptions(self):
        return await self.subscription_repository.get_subscriptions()

    async def change_subscription_status(self, subscription_id: int, status: SubscriptionStatus):
        await self.subscription_repository.change_status(subscription_id, status)
        if status == SubscriptionStatus.active:
            subscription = await self.subscription_repository.get_subscription(subscription_id)
            if subscription_id not in tasks:
                task = SubscriptionWorker(subscription, self.account_service, self.subscription_repository)
                tasks[subscription.id] = asyncio.create_task(task.run())
        else:
            if subscription_id in tasks:
                task = tasks.get(subscription_id)
                task.cancel()
                tasks.pop(subscription_id)
