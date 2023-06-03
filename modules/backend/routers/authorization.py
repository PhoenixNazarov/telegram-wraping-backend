from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel

from modules.backend.backend_controller import BackendController

from modules.backend.config import PASSWORDS

router = APIRouter(prefix='/authorization')


class AuthorizationDto(BaseModel):
    username: str
    password: str


@router.post('/')
async def authorize(request: Request, authorization_dto: AuthorizationDto):
    print(request.headers)
    for k, v in PASSWORDS.items():
        if v['username'] == authorization_dto.username and v['password'] == authorization_dto.password:
            return {'key': k, 'name': v['name']}
    raise HTTPException(status_code=503, detail="Not auth")
