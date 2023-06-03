import time
from typing import Optional

from pydantic import BaseModel

from modules.accounts.entity.account import AccountCategory


class Parsing(BaseModel):
    id: Optional[int]
    account_id: int

    link: str
    image_dir: Optional[str]

    time_delay: int = 5
    time_delay_get_user: int = 1
    limit: Optional[int]
    block: int = 20
    current_offset: int = 0

    time_start: int = int(time.time())

    categories: list[str] = []
