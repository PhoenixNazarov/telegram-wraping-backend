from typing import Optional

from fastapi import APIRouter, Request, Response
from pydantic import BaseModel

from modules.backend.backend_controller import BackendController

router = APIRouter(prefix='/names')


class ChangeNameDto(BaseModel):
    name_id: int
    first_name: Optional[str]
    last_name: Optional[str]
    username: Optional[str]
    about: Optional[str]
    categories: list[str]


class NameDto(BaseModel):
    name_id: int


@router.get('/image/{user_id}')
async def get_image(request: Request, user_id: int):
    controller: BackendController = request.scope['controller']
    return Response(content=await controller.get_names_image(user_id), media_type="image/png")


@router.get('/active')
async def get_names(request: Request):
    controller: BackendController = request.scope['controller']
    return await controller.get_names()


@router.post('/edit')
async def get_names(request: Request, edit_dto: ChangeNameDto):
    controller: BackendController = request.scope['controller']
    return await controller.edit_name(
        edit_dto.name_id,
        edit_dto.first_name,
        edit_dto.last_name,
        edit_dto.about,
        edit_dto.username,
        edit_dto.categories
    )


@router.post('/delete')
async def get_names(request: Request, name_dto: NameDto):
    controller: BackendController = request.scope['controller']
    return await controller.delete_name(name_dto.name_id)
