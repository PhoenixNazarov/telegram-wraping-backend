import asyncio

import requests

from modules.proxy.proxy_repository import ProxyRepository


class ProxyChecker:
    def __init__(self, proxy_repository: ProxyRepository):
        self.proxy_repository = proxy_repository

    async def run(self):
        while 1:
            proxies = await self.proxy_repository.get_proxies()

            for proxy in proxies:
                p = f'{proxy.username}:{proxy.password}@{proxy.addr}:{proxy.port}' if proxy.auth \
                    else f'{proxy.addr}:{proxy.port}'
                print(p)
                try:
                    # resp = requests.get('https://www.google.com',
                    #                     proxies=dict(http='socks5://' + p,
                    #                                  https='socks5://' + p),
                    #                     timeout=10,
                    #                     )
                    print('active')
                    await self.proxy_repository.change_proxy_status(proxy.id, True)
                except:
                    await self.proxy_repository.change_proxy_status(proxy.id, False)
            await asyncio.sleep(5)
