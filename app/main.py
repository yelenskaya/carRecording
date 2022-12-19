from fastapi import FastAPI
from socketio import ASGIApp, AsyncServer

from app.events import recording_namespace
from app.routes import router

app = FastAPI()
app.include_router(router)

socket_server = AsyncServer(cors_allowed_origins='*', async_mode='asgi')
socket_app = ASGIApp(socket_server, app)
app.mount('/ws', socket_app)

socket_server.register_namespace(recording_namespace)
