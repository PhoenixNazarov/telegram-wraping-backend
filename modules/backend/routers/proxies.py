from fastapi import APIRouter, Request
from pydantic import BaseModel

from modules.backend.backend_controller import BackendController

router = APIRouter(prefix='/proxy')


class ProxyIdDto(BaseModel):
    proxy_id: int


class ProxyDto(BaseModel):
    proxy: str
    categories: list[str]


@router.get('/get')
async def get_proxy(request: Request):
    controller: BackendController = request.scope['controller']
    return await controller.get_proxies()


@router.post('/add')
async def add_proxy(request: Request, proxy_dto: ProxyDto):
    controller: BackendController = request.scope['controller']
    return await controller.add_proxies(proxy_dto.proxy, proxy_dto.categories)


@router.post('/remove')
async def save_proxy(request: Request, proxy_dto: ProxyIdDto):
    controller: BackendController = request.scope['controller']
    return await controller.remove_proxy(proxy_dto.proxy_id)
