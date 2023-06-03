from typing import Optional

from fastapi import APIRouter, Request, Response, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel

from modules.backend.backend_controller import BackendController

router = APIRouter(prefix='/accounts')


class ChangeUserDto(BaseModel):
    user_id: int
    first_name: Optional[str]
    last_name: Optional[str]
    username: Optional[str]
    about: Optional[str]
    categories: list[str]


class UserDto(BaseModel):
    user_id: int


class CategoryDto(BaseModel):
    category: str


class ImportCategories(BaseModel):
    categories: Optional[str]
    # file: UploadFile


@router.get('/image/{user_id}')
async def get_image(request: Request, user_id: int):
    controller: BackendController = request.scope['controller']
    return Response(content=await controller.get_image(user_id), media_type="image/png")


@router.post('/import')
async def import_session(request: Request):
    form = await request.form()
    file = form['file']
    categories = form['categories']
    controller: BackendController = request.scope['controller']
    out = await controller.import_session(await file.read(), categories.split(" "))
    if not out:
        raise HTTPException(status_code=500, detail='cant auth')


@router.get('/active')
async def get_active_accounts(request: Request):
    controller: BackendController = request.scope['controller']
    return await controller.get_accounts(active=True)


@router.get('/inactive')
async def edit_inactive_accounts(request: Request):
    controller: BackendController = request.scope['controller']
    return await controller.get_accounts(active=False)


@router.get('/active_ids')
async def edit_active_accounts_ids(request: Request):
    controller: BackendController = request.scope['controller']
    return await controller.get_active_accounts_ids()


@router.post('/edit')
async def edit_account(request: Request, change_user_dto: ChangeUserDto):
    controller: BackendController = request.scope['controller']
    return await controller.change_account(
        change_user_dto.user_id,
        change_user_dto.first_name,
        change_user_dto.last_name,
        change_user_dto.about,
        change_user_dto.username,
        change_user_dto.categories
    )


@router.post('/update')
async def update_account(request: Request, user_dto: UserDto):
    controller: BackendController = request.scope['controller']
    return await controller.update_account(user_dto.user_id)


@router.post('/check')
async def check_account(request: Request, user_dto: UserDto):
    controller: BackendController = request.scope['controller']
    return await controller.check_account(user_dto.user_id)


@router.get('/download_session/{user_id}')
async def download_session(request: Request, user_id: int):
    controller: BackendController = request.scope['controller']
    return FileResponse(await controller.get_session(user_id))


@router.get('/categories')
async def get_categories(request: Request):
    controller: BackendController = request.scope['controller']
    return await controller.get_categories()


@router.post('/add_category')
async def add_categories(request: Request, category_dto: CategoryDto):
    controller: BackendController = request.scope['controller']
    return await controller.add_category(category_dto.category)


@router.post('/remove_category')
async def remove_categories(request: Request, category_dto: CategoryDto):
    controller: BackendController = request.scope['controller']
    return await controller.remove_category(category_dto.category)
