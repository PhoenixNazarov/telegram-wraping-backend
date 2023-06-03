from abc import ABC, abstractmethod

from modules.proxy.entity.proxy import Proxy


class ProxyRepository(ABC):
    @abstractmethod
    async def get_random_proxy(self) -> Proxy:
        pass

    @abstractmethod
    async def get_proxies(self) -> list[Proxy]:
        pass

    @abstractmethod
    async def add_proxies(self, proxies: list[Proxy]):
        pass

    @abstractmethod
    async def remove_proxy(self, proxy_id: int):
        pass

    @abstractmethod
    async def change_proxy_status(self, proxy_id: int, active: bool):
        pass
