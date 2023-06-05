import random
from enum import Enum
from typing import Optional

from pydantic import BaseModel, validator

# Desktop
api_id = 2040
api_hash = "b18441a1ff607e10a989891a5462e627"

samsung_models = [
    'SM-G990',
    'SM-S901', 'SM-S906', 'SM-S908', 'SM-A135', 'SM-A235', 'SM-E236', 'SM-A536', 'SM-M236', 'SM-A336', 'SM-A736',
    'SM-M336', 'SM-M536', 'SM-E135', 'SM-M135', 'SM-G736', 'SM-F721', 'SM-F936B', 'SM-A047', 'SM-A045', 'SM-A042',
    'SM-M045'
    'SM-E045'
    'SM-A146',
    'SM-S911x',
    'SM-S916x',
    'SM-S918x'
]


class AccountDeviceData(BaseModel):
    api_id: int
    api_hash: str
    device_model: str
    system_version: str
    app_version: str
    lang_code: str
    system_lang_code: str


def generate() -> AccountDeviceData:
    lang = random.choice(['ru', 'en', 'us', 'id'])
    return AccountDeviceData(
        api_id=21724,
        api_hash="3e0cb5efcd52300aec5994fdfc5bdc16",
        device_model="Samsung" + random.choice(samsung_models),
        system_version="SDK" + random.choice(['31', '32', '33']),
        app_version=random.choice(
            ['9.6.0 (3319)', '9.4.0 (3098)', '9.3.0 (3021)', '9.2.1 (2962)', '9.1.0 (2885)', '8.8.2 (2702)']),
        lang_code=lang,
        system_lang_code=lang
    )


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

    account_device: AccountDeviceData = generate()

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
