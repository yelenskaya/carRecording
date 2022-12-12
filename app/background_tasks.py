from asyncio import sleep
from csv import reader
from logging import getLogger

from botocore.response import StreamingBody

from app.events import send_record

logger = getLogger(__name__)


async def reproduce_recording(recording_id: str, file: StreamingBody):
    lines = file.read().decode('utf-8').splitlines(True)

    logger.info(f'Started to reproduce recording {recording_id}')
    last_timestamp = 0
    for line in reader(lines[1:]):
        timestamp, record = line
        await send_record(record, recording_id)

        time_difference = (int(timestamp) - last_timestamp) / 1000
        await sleep(time_difference)

        last_timestamp = int(timestamp)

    logger.info(f'Finished reproducing recording {recording_id}')
