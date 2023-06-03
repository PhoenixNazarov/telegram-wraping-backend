import random

import socks

from modules.proxy.entity.proxy import Proxy
from modules.proxy.proxy_repository import ProxyRepository


class ProxyService:
    def __init__(self, proxy_repository: ProxyRepository):
        self.proxy_repository = proxy_repository

    async def add_proxies(self, proxies: list[str], categories: list[str] = []):
        prxs = []
        for i in proxies:
            if '@' in i:
                username, password = i.split('@')[0].split(':')
                addr, port = i.split('@')[1].split(':')
                prxs.append(Proxy(addr=addr, port=int(port), auth=True, username=username, password=password,
                                  categories=categories))
            else:
                addr, port = i.split(':')
                prxs.append(Proxy(addr=addr, port=int(port), auth=False, categories=categories))
        await self.proxy_repository.add_proxies(prxs)

    async def get_random_proxy(self, category: list[str] = []):
        proxy = await self.proxy_repository.get_proxies()
        if len(proxy) <= 0:
            raise ValueError
        proxy = list(filter(lambda i: i.active, proxy))
        avaible = []
        if len(category) > 0:
            for p in proxy:
                if len(p.categories) > 0:
                    if any([c in category for c in p.categories]):
                        avaible.append(p)

        if len(avaible) > 0:
            proxy = random.choice(avaible)
        else:
            proxy = random.choice(proxy)

        if proxy.auth:
            return socks.SOCKS5, proxy.addr, proxy.port, True, proxy.username, proxy.password
        else:
            return socks.SOCKS5, proxy.addr, proxy.port

    async def get_proxies(self):
        return await self.proxy_repository.get_proxies()

    async def remove_proxy(self, proxy_id: int):
        return await self.proxy_repository.remove_proxy(proxy_id)
