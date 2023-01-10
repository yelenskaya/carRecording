from asyncio import sleep
from csv import reader
from enum import auto, StrEnum
from logging import getLogger
from time import time

from botocore.response import StreamingBody
from orjson import orjson
from pydantic import BaseModel, Field

from app.dependencies import get_redis
from app.events import recording_namespace

logger = getLogger(__name__)


class RecordLockedError(Exception):
    pass


class ReplayStatus(StrEnum):
    IN_PROGRESS = auto()
    FINISHED = auto()


def orjson_dumps(v, *, default):
    return orjson.dumps(v, default=default).decode()


class Replay(BaseModel):
    status: ReplayStatus
    last_timestamp_in_ms: int = Field(default_factory=lambda: int(time() * 1000))

    class Config:
        json_loads = orjson.loads
        json_dumps = orjson_dumps


class LockRecording:
    def __init__(self, recording_id: str):
        self.recording_id = recording_id
        self.connection = get_redis()

    async def __aenter__(self):
        replay = await self.connection.get(self.recording_id)

        if replay and Replay.parse_raw(replay).status == ReplayStatus.IN_PROGRESS:
            logger.error(f'Replay of the recording {self.recording_id} is in progress, cannot start a new one')
            raise RecordLockedError('Another replay is in progress')

        await self.connection.set(self.recording_id, Replay(status=ReplayStatus.IN_PROGRESS).json())

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        replay = Replay.parse_raw(await self.connection.get(self.recording_id))
        replay.status = ReplayStatus.FINISHED

        await self.connection.set(self.recording_id, replay.json())


async def reproduce_recording(recording_id: str, file: StreamingBody):
    async with LockRecording(recording_id):
        lines = file.read().decode('utf-8').splitlines(True)

        logger.info(f'Started to reproduce recording {recording_id}')
        last_timestamp = 0
        for line in reader(lines[1:]):
            timestamp, record = line
            await recording_namespace.send_record(record, recording_id)

            time_difference = (int(timestamp) - last_timestamp) / 1000
            await sleep(time_difference)

            last_timestamp = int(timestamp)

        logger.info(f'Finished reproducing recording {recording_id}')
