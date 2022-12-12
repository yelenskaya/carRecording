from csv import reader
from io import StringIO

from fastapi import UploadFile
from orjson import JSONDecodeError, loads
from pydantic import ValidationError

from app.schemas import RecordSchema

CSV_HEADERS = ('timestamp', 'data')


class FileValidationError(Exception):
    pass


async def validate_file(upload_file: UploadFile):
    _validate_file_extension(upload_file.filename)

    last_timestamp = 0

    file_object = await upload_file.read()

    csv_reader = reader(StringIO(file_object.decode()))

    _validate_headers(next(csv_reader))

    for line_number, line in enumerate(csv_reader, start=1):
        timestamp, data = _parse_row(line, line_number)

        _check_timeline(timestamp, last_timestamp, line_number)
        record = _validate_record(timestamp, data, line_number)

        last_timestamp = record.timestamp

    await upload_file.seek(0)


def _validate_file_extension(file_name: str):
    if not file_name.endswith('.csv'):
        raise FileValidationError(f'Only csv files are accepted, got {file_name}')


def _validate_headers(headers: list[str]):
    if not tuple(headers) == CSV_HEADERS:
        raise FileValidationError(f'File headers are invalid. Allowed headers are {CSV_HEADERS}, got {headers}')


def _parse_row(line: str, line_number: int) -> tuple[int, dict]:
    try:
        timestamp, data = line
    except ValueError:
        raise FileValidationError(f'File is invalid. Incorrect number of fields in line {line_number}')

    try:
        timestamp = int(timestamp)
    except ValueError:
        raise FileValidationError(f'File is invalid. Timestamp must be an int in line {line_number}')

    try:
        data = loads(data)
    except JSONDecodeError:
        raise FileValidationError(f'File is invalid. Data must be a valid json in line {line_number}')

    return timestamp, data


def _check_timeline(timestamp: int, last_timestamp: int, line_number: int):
    if timestamp < last_timestamp:
        raise FileValidationError(
            f'File is invalid. Timestamp in line {line_number} must be greater than the previous one'
        )


def _validate_record(timestamp: int, data: dict, line_number: int) -> RecordSchema:
    try:
        record = RecordSchema(timestamp=timestamp, data=data)
    except ValidationError as e:
        raise FileValidationError(f'File is invalid. Data error in line {line_number} \n {str(e)}')
    return record
