from fastapi import FastAPI
from socketio import ASGIApp, AsyncServer

from app.background_tasks import mark_interrupted_recordings
from app.dependencies import get_redis
from app.events import recording_namespace
from app.routes import router

app = FastAPI()
app.include_router(router)

socket_server = AsyncServer(cors_allowed_origins='*', async_mode='asgi')
socket_app = ASGIApp(socket_server, app)
app.mount('/ws', socket_app)

socket_server.register_namespace(recording_namespace)


@app.on_event('startup')
async def startup_event():
    await mark_interrupted_recordings()


@app.on_event('shutdown')
async def shutdown_event():
    await get_redis().close()
