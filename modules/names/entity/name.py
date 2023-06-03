from pathlib import Path
from typing import Optional

from pydantic import BaseModel, validator

from modules.accounts.entity.account import AccountCategory


class Name(BaseModel):
    id: int

    first_name: Optional[str]
    last_name: Optional[str]
    about: Optional[str]
    username: Optional[str]
    new_username: Optional[str]
    image: Optional[str | bytes]

    categories: list[str] = []

    @validator('image')
    def passwords_match(cls, v):
        if v:
            return str(Path(v))
