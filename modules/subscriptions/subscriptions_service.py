import asyncio
import random

from modules.accounts.account_control_service import AccountControlService
from modules.subscriptions.entity.subscription import Subscription, SubscriptionUnit, SubscriptionStatus
from modules.subscriptions.subscription_worker import SubscriptionWorker
from modules.subscriptions.subscriptions_repository import SubscriptionRepository
import random
tasks = {}


class SubscriptionsService:
    def __init__(self, account_service: AccountControlService, subscription_repository: SubscriptionRepository):
        self.account_service = account_service
        self.subscription_repository = subscription_repository

    async def create_subscription(self, link: str, timeline: list[(int, int, int)], categories: list[str] = None,
                                  exclude_categories: list[str] = None):
        if not categories:
            categories = []
        if not exclude_categories:
            exclude_categories = []

        categories = list((set(categories) | set(exclude_categories)) ^ set(exclude_categories))
        subscription = Subscription(link=link, categories=categories)
        for i in timeline:
            for j in range(i[2]):
                unit = SubscriptionUnit(time_delay=random.randint(i[0], i[1]))
                subscription.timeline.append(unit)
        return await self.subscription_repository.save_subscription(subscription)

    async def edit_subscription(self, subscription_id: int, timeline: list[(int, int, int)]):
        subscription = await self.subscription_repository.get_subscription(subscription_id)
        count = timeline[2]
        if count > 0:
            new_timeline = subscription.timeline
            for j in range(count):
                unit = SubscriptionUnit(time_delay=random.randint(timeline[0], timeline[1]))
                new_timeline.append(unit)
            subscription.timeline = new_timeline
            await self.subscription_repository.save_subscription(subscription)
        elif count < 0:
            new_timeline = []
            ava_timeline = []
            for u in subscription.timeline:
                if not (timeline[0] <= u.time_delay <= timeline[1]):
                    new_timeline.append(u)
                else:
                    ava_timeline.append(u)
            while count != 0 and len(ava_timeline) > 0:
                for u in ava_timeline:
                    if random.random() < 0.2:
                        ava_timeline.remove(u)
                        count += 1
                        if count == 0:
                            break
            subscription.timeline = new_timeline + ava_timeline
            await self.subscription_repository.save_subscription(subscription)

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
