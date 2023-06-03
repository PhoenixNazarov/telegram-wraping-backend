from fastapi import Request, HTTPException
from starlette.types import ASGIApp, Scope, Receive, Send

from modules.backend.backend_controller import BackendController
from modules.backend.config import PASSWORDS
from modules.utils.service_factories import create_account_control_service, create_parsing_service, \
    create_names_service, create_subscriptions_service, create_proxy_service


class SessionASGIMiddleware:
    def __init__(self, app: ASGIApp):
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        request = Request(scope, receive)
        auth_key = request.headers.get('authorization')
        if '/image' not in request.url.path:
            if auth_key not in PASSWORDS and request.url.path not in ['/authorization', '/authorization/',
                                                                      '/accounts/import', '/accounts/import/']:
                raise HTTPException(status_code=503, detail='not authorized')
        exception = None

        try:
            controller = BackendController(
                create_account_control_service(),
                create_parsing_service(),
                create_names_service(),
                create_subscriptions_service(),
                create_proxy_service()
            )
            request.scope['controller'] = controller

            await self.app(request.scope, request.receive, send)
        except Exception as e:
            exception = e
        finally:
            pass

        if exception:
            raise exception
