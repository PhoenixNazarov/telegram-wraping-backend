from fastapi import APIRouter, Request
from pydantic import BaseModel

from modules.backend.backend_controller import BackendController
from modules.subscriptions.entity.subscription import SubscriptionStatus

router = APIRouter(prefix='/subscriptions')


class CreateSubscriptionDto(BaseModel):
    link: str
    join_link: bool
    timeline: list[list[int]]
    categories: list[str]
    exclude_categories: list[str]


class ChangeSubscriptionDto(BaseModel):
    subscription_id: int
    status: SubscriptionStatus


class EditSubscriptionDto(BaseModel):
    subscription_id: int
    start: int
    end: int
    count: int


@router.get('/active')
async def get_subscriptions(request: Request):
    controller: BackendController = request.scope['controller']
    return await controller.get_subscriptions()


@router.post('/create')
async def create_subscription(request: Request, start_parsing_dto: CreateSubscriptionDto):
    controller: BackendController = request.scope['controller']
    return await controller.create_subscription(start_parsing_dto.link, start_parsing_dto.join_link,
                                                start_parsing_dto.timeline,
                                                start_parsing_dto.categories, start_parsing_dto.exclude_categories)


@router.post('/status')
async def change_subscription(request: Request, change_subscription_dto: ChangeSubscriptionDto):
    controller: BackendController = request.scope['controller']
    return await controller.edit_subscription(change_subscription_dto.subscription_id, change_subscription_dto.status)


@router.post('/edit')
async def edit_subscription(request: Request, edit_subscription_dto: EditSubscriptionDto):
    controller: BackendController = request.scope['controller']
    return await controller.edit_subscription_count(edit_subscription_dto.subscription_id, (
        edit_subscription_dto.start, edit_subscription_dto.end, edit_subscription_dto.count))
