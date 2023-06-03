import json
import os
import random
from pathlib import Path
from typing import Optional

from modules.proxy.entity.proxy import Proxy
from modules.proxy.proxy_repository import ProxyRepository


def write_if_not_exist(path, string):
    if not os.path.exists(path):
        with open(path, 'w') as file:
            file.write(string)


class ProxyRepositoryJson(ProxyRepository):
    def __init__(self, path: str):
        self.path = Path(path)
        write_if_not_exist(self.path, '[]')

    def get_base(self):
        with open(self.path, 'r') as file:
            return json.loads(file.read())

    def save_base(self, data):
        with open(self.path, 'w') as file:
            file.write(json.dumps(data))

    async def get_random_proxy(self) -> Optional[Proxy]:
        data = self.get_base()
        if len(data) == 0:
            return None
        return Proxy.parse_raw(random.choice(data))

    async def get_proxies(self) -> list[Proxy]:
        data = self.get_base()
        return [Proxy.parse_raw(i) for i in data]

    async def add_proxies(self, proxies: list[Proxy]):
        data = await self.get_proxies()
        for i in proxies:
            ids = []
            for p in data:
                ids.append(p.id)
            if ids:
                i.id = max(ids) + 1
            else:
                i.id = 1
            data.append(i)
        self.save_base([i.json() for i in data])

    async def remove_proxy(self, proxy_id: int):
        data = await self.get_proxies()
        data = list(filter(lambda i: i.id != proxy_id, data))
        self.save_base([i.json() for i in data])

    async def change_proxy_status(self, proxy_id: int, active: bool):
        data = await self.get_proxies()
        for i in data:
            if i.id == proxy_id:
                i.active = active
                break
        self.save_base([i.json() for i in data])
