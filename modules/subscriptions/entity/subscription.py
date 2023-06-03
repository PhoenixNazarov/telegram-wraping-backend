from enum import Enum
from typing import Optional

from pydantic import BaseModel


class SubscriptionStatus(str, Enum):
    pause = "pause"
    active = "active"
    finished = "finished"


class SubscriptionResult(str, Enum):
    wait = "wait"
    process = "process"
    success = "success"
    already = "already"
    failed = "failed"


class SubscriptionUnit(BaseModel):
    id: Optional[int]
    account_id: Optional[int]
    time_delay: int
    result: SubscriptionResult = SubscriptionResult.wait


class Subscription(BaseModel):
    id: Optional[int]
    link: str
    current_time: int = 0
    timeline: list[SubscriptionUnit] = []

    status: SubscriptionStatus = SubscriptionStatus.pause
    categories: list[str]
