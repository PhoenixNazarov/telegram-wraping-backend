import time

import uvicorn
from fastapi import FastAPI, Request
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.gzip import GZipMiddleware

from modules.backend.config import host, port
from modules.backend.middleware import asgi_session
from modules.backend.routers import accounts, parsing, names, subscriptions, authorization, proxies

app = FastAPI(title='TelegramWrapping', docs_url=None, redoc_url=None, openapi_url=None,
              swagger_ui_oauth2_redirect_url=None)


@app.get("/")
async def root():
    return int(time.time())


@app.exception_handler(Exception)
async def exception_handler(request: Request, exc: Exception):
    try:
        raise exc
    except Exception as e:
        print(e)


# Middlewares
app.add_middleware(asgi_session.SessionASGIMiddleware)
origins = [
    "http://localhost",
    "http://localhost:5050",
    "http://localhost:5050/",
    "http://localhost:5173",
    "http://localhost:5173/",
    "http://85.234.106.73:5050",
    "http://85.234.106.73:5050/",
    "http://80.90.184.66:5050",
    "http://80.90.184.66:5050/",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Routers
app.include_router(authorization.router)
app.include_router(accounts.router)
app.include_router(parsing.router)
app.include_router(names.router)
app.include_router(subscriptions.router)
app.include_router(proxies.router)

uvicorn.run(app, host=host, port=port)
