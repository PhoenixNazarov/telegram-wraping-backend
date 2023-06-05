import asyncio
import random
import time

from modules.accounts.account_control_service import AccountControlService
from modules.subscriptions.entity.subscription import Subscription, SubscriptionStatus, SubscriptionResult, \
    SubscriptionUnit
from modules.subscriptions.subscriptions_repository import SubscriptionRepository


class SubscriptionWorker:
    def __init__(self,
                 subscription: Subscription,
                 account_control_service: AccountControlService,
                 subscriptions_repository: SubscriptionRepository):
        self.subscription = subscription
        self.account_control_service = account_control_service
        self.subscriptions_repository = subscriptions_repository
        self.tasks = []

    async def subscribe(self, unit: SubscriptionUnit, account_id: int):
        try:
            out = await self.account_control_service.subscribe_channel_by_link(account_id, self.subscription.link,
                                                                               self.subscription.join_link)
            print(out)
        except Exception as e:
            print('exc')
            out = 2

        if out == 0:
            await self.subscriptions_repository.change_unit_status(self.subscription.id,
                                                                   unit.id,
                                                                   account_id,
                                                                   SubscriptionResult.success)
        elif out == 1:
            await self.subscriptions_repository.change_unit_status(self.subscription.id,
                                                                   unit.id,
                                                                   None,
                                                                   SubscriptionResult.wait)
            await self.subscriptions_repository.add_unit(self.subscription.id,
                                                         account_id,
                                                         SubscriptionResult.already)
        elif out == 2:
            await self.subscriptions_repository.change_unit_status(self.subscription.id,
                                                                   unit.id,
                                                                   None,
                                                                   SubscriptionResult.wait)
        else:
            await self.subscriptions_repository.change_unit_status(self.subscription.id,
                                                                   unit.id,
                                                                   None,
                                                                   SubscriptionResult.wait)
            await self.subscriptions_repository.add_unit(self.subscription.id,
                                                         account_id,
                                                         SubscriptionResult.failed)

    async def run(self):
        while True:
            self.subscription = await self.subscriptions_repository.get_subscription(self.subscription.id)
            if not self.subscription:
                return
            if self.subscription.status != SubscriptionStatus.active:
                return

            need_subscribe = list(
                filter(
                    lambda i: i.result == SubscriptionResult.wait,
                    self.subscription.timeline
                )
            )

            need_fix_subscribe = list(
                filter(
                    lambda i: i.result == SubscriptionResult.process,
                    self.subscription.timeline
                )
            )

            if len(need_subscribe) + len(need_fix_subscribe) <= 0:
                await self.subscriptions_repository.change_status(self.subscription.id, SubscriptionStatus.finished)
                return

            need_start_subscribe = list(
                filter(
                    lambda i: i.time_delay - time.time() <= 5,
                    need_subscribe
                )
            )

            need_start_fix_subscribe = list(
                filter(
                    lambda i: time.time() - i.time_delay >= 30,
                    need_fix_subscribe
                )
            )

            subscribe_users = list(map(lambda i: i.account_id, self.subscription.timeline))
            suit_users = list(
                filter(
                    lambda i: i.user_id not in subscribe_users,
                    await self.account_control_service.get_accounts(categories=self.subscription.categories)
                )
            )

            random.shuffle(suit_users)
            for i in need_start_subscribe + need_start_fix_subscribe:
                if len(suit_users) <= 0:
                    if len(need_fix_subscribe) > 0:
                        break
                    await self.subscriptions_repository.change_status(self.subscription.id,
                                                                      SubscriptionStatus.finished)
                    return
                user = suit_users.pop(0)
                await self.subscriptions_repository.change_unit_status(self.subscription.id,
                                                                       i.id,
                                                                       user.user_id,
                                                                       SubscriptionResult.process)
                self.tasks.append(asyncio.create_task(self.subscribe(i, user.user_id)))
                await asyncio.sleep(0.5)
            await asyncio.sleep(5)
