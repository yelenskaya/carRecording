from logging import getLogger

from socketio import AsyncServer

socket_server = AsyncServer(cors_allowed_origins='*', async_mode='asgi')
logger = getLogger(__name__)


@socket_server.event
async def connect(sid: str, environ: dict):
    logger.info(f'connected {sid}')


@socket_server.event
async def disconnect(sid: str):
    logger.info(f'disconnected {sid}')


@socket_server.event
async def join(sid: str, room: str):
    socket_server.enter_room(sid, room)
    logger.info(f'joined room {room}')


async def send_record(record: str, recording_id: str):
    await socket_server.emit('reproduce', data=record, room=recording_id)
