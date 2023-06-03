import json
import os
import time
from typing import Optional

from modules.subscriptions.entity.subscription import Subscription, SubscriptionResult, SubscriptionStatus, \
    SubscriptionUnit
from modules.subscriptions.subscriptions_repository import SubscriptionRepository


def write_if_not_exist(path, string):
    if not os.path.exists(path):
        with open(path, 'w') as file:
            file.write(string)


class SubscriptionRepositoryJson(SubscriptionRepository):
    def __init__(self, path: str):
        self.path = path
        write_if_not_exist(path, '{"id": 1, "subscriptions": {}}')

    def get_base(self):
        with open(self.path, 'r') as file:
            return json.loads(file.read())

    def save_base(self, data):
        with open(self.path, 'w') as file:
            file.write(json.dumps(data))

    async def save_subscription(self, subscription: Subscription) -> Subscription:
        base = self.get_base()
        if not subscription.id:
            subscription.id = base['id']
            base['id'] += 1
        for i in range(len(subscription.timeline)):
            subscription.timeline[i].id = i
        base['subscriptions'][str(subscription.id)] = subscription.json()
        self.save_base(base)
        return subscription

    async def get_subscriptions(self) -> list[Subscription]:
        base = self.get_base()
        return [Subscription.parse_raw(i) for i in base['subscriptions'].values()][-10:]

    async def get_subscription(self, subscription_id: int) -> Optional[Subscription]:
        base = self.get_base()
        if str(subscription_id) in base['subscriptions']:
            return Subscription.parse_raw(base['subscriptions'][str(subscription_id)])

    async def change_unit_status(self, subscription_id: int, unit_id: int, account_id: int, status: str):
        base = self.get_base()
        if str(subscription_id) in base['subscriptions']:
            subscription = Subscription.parse_raw(base['subscriptions'][str(subscription_id)])
            for i in subscription.timeline:
                if i.id == unit_id:
                    i.account_id = account_id
                    i.result = SubscriptionResult(status)
                    base['subscriptions'][str(subscription.id)] = subscription.json()
                    self.save_base(base)
                    break

    async def add_unit(self, subscription_id: int, account_id: int, status: str):
        base = self.get_base()
        if str(subscription_id) in base['subscriptions']:
            subscription = Subscription.parse_raw(base['subscriptions'][str(subscription_id)])
            subscription.timeline.append(
                SubscriptionUnit(id=len(subscription.timeline),
                                 account_id=account_id,
                                 time_delay=int(time.time()),
                                 result=SubscriptionResult(status))
            )
            base['subscriptions'][str(subscription_id)] = subscription.json()
            print('add', SubscriptionResult(status))
            self.save_base(base)

    async def change_current_time(self, subscription_id: int, current_time: int):
        base = self.get_base()
        if str(subscription_id) in base['subscriptions']:
            subscription = Subscription.parse_raw(base['subscriptions'][str(subscription_id)])
            subscription.current_time = current_time
            base['subscriptions'][str(subscription.id)] = subscription.json()
            self.save_base(base)

    async def change_status(self, subscription_id: int, status: str):
        base = self.get_base()
        if str(subscription_id) in base['subscriptions']:
            subscription = Subscription.parse_raw(base['subscriptions'][str(subscription_id)])
            subscription.status = SubscriptionStatus(status)
            base['subscriptions'][str(subscription.id)] = subscription.json()
            self.save_base(base)
