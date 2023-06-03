from typing import Optional

from pydantic import BaseModel


class Proxy(BaseModel):
    id: Optional[int]

    addr: str
    port: int

    auth: bool
    username: Optional[str]
    password: Optional[str]

    active: Optional[bool]
    categories: list[str] = []
