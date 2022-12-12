from fastapi import FastAPI
from socketio import ASGIApp

from app.events import socket_server
from app.routes import router

app = FastAPI()
app.include_router(router)

socket_app = ASGIApp(socket_server, app)
app.mount('/ws', socket_app)
