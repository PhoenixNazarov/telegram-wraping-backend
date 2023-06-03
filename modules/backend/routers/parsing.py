from typing import Optional

from fastapi import APIRouter, Request
from pydantic import BaseModel

from modules.backend.backend_controller import BackendController

router = APIRouter(prefix='/parsing')


class StartParsingDto(BaseModel):
    link: str
    limit: Optional[int]
    block: int
    delay_block: int
    delay_users: int
    user: int
    categories: list[str]


@router.get('/active')
async def get_parsing(request: Request):
    controller: BackendController = request.scope['controller']
    return await controller.get_actual_parsing()


@router.post('/start')
async def start_parsing(request: Request, start_parsing_dto: StartParsingDto):
    controller: BackendController = request.scope['controller']
    return await controller.start_parsing(start_parsing_dto.link, start_parsing_dto.limit, start_parsing_dto.block,
                                          start_parsing_dto.delay_block, start_parsing_dto.delay_users,
                                          start_parsing_dto.user, start_parsing_dto.categories)


@router.get('/stop')
async def stop_parsing(request: Request):
    controller: BackendController = request.scope['controller']
    return await controller.stop_parsing()
