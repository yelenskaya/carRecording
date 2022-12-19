from logging import getLogger

from socketio import AsyncNamespace

logger = getLogger(__name__)


class CarRecordingNamespace(AsyncNamespace):
    def on_connect(self, sid: str, environ: dict):
        logger.info(f'connected {sid}')

    def on_disconnect(self, sid: str):
        logger.info(f'disconnected {sid}')

    async def on_join(self, sid: str, room: str):
        self.enter_room(sid, room, namespace=self.namespace)
        logger.info(f'joined room {room}')

    async def send_record(self, record: str, recording_id: str):
        await self.emit('reproduce', data=record, room=recording_id, namespace=self.namespace)


recording_namespace = CarRecordingNamespace('/recording')
