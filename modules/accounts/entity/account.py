from enum import Enum
from typing import Optional

from pydantic import BaseModel, validator


class AccountStatus(str, Enum):
    active = 'active'
    inactive = 'inactive'


class AccountCategory(str, Enum):
    male = 'male'
    female = 'female'
    not_changed = "not_changed"
    autoreg_lolz = "autoreg_lolz"


class Account(BaseModel):
    user_id: Optional[int]
    phone: Optional[str]

    first_name: Optional[str]
    last_name: Optional[str]
    about: Optional[str]
    username: Optional[str]

    session: Optional[str]
    image: Optional[str]

    status: AccountStatus = AccountStatus.inactive
    inactive_reason: Optional[str] = ''
    inactive_date: Optional[int] = 0

    categories: list[str] = []

    channel_join: int = 0

    @validator('categories')
    def category_set(cls, v):
        v = list(set(v))
        if '' in v:
            v.remove('')

        if ' ' in v:
            v.remove(' ')
        return v

    class Config:
        validate_assignment = True
