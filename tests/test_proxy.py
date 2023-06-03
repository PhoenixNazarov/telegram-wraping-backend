import pytest

from modules.proxy.entity.proxy import Proxy
from modules.utils.service_factories import create_proxy_service, create_proxy_repository

cid = 0


@pytest.mark.asyncio
async def test_simple(mocker):
    with pytest.raises(ValueError):
        proxy = await create_proxy_service().get_random_proxy()
    await create_proxy_service().add_proxies(["asd:pass@8.8.8.8:80", "1.1.1.1:1"], categories=['asd'])
    proxies = await create_proxy_service().get_proxies()
    assert proxies == [
        Proxy(id=1, addr='8.8.8.8', port=80, auth=True, username='asd', password='pass', active=None, categories=['asd']),
        Proxy(id=2, addr='1.1.1.1', port=1, auth=False, username=None, password=None, active=None, categories=['asd'])]

    await create_proxy_service().add_proxies(["asd:pass@8.8.8.8:81"], ['www'])
    for p in await create_proxy_service().get_proxies():
        await create_proxy_repository().change_proxy_status(p.id, True)
    assert await create_proxy_service().get_random_proxy(["www"]) == (2, '8.8.8.8', 81, True, 'asd', 'pass')

    assert await create_proxy_service().get_random_proxy(["asd"]) in [(2, '1.1.1.1', 1),
                                                                      (2, '8.8.8.8', 80, True, 'asd', 'pass')]


@pytest.mark.asyncio
async def test_random(mocker):
    proxy = await create_proxy_service().get_random_proxy()
    await create_proxy_service().add_proxies(["1.1.1.1:2", "1.1.1.1:3", "1.1.1.1:5", "1.1.1.1:6"])
    for p in await create_proxy_service().get_proxies():
        await create_proxy_repository().change_proxy_status(p.id, True)

    for i in range(20):
        print(await create_proxy_service().get_random_proxy(["qweqwe"]))

