import logging
from uuid import uuid4

from botocore.exceptions import ClientError
from fastapi import APIRouter, Depends, HTTPException, UploadFile

from app.dependencies import get_s3_client, get_settings
from app.file_validation import FileValidationError, validate_file
from app.schemas import S3RecordingSchema

router = APIRouter(prefix="/recordings", tags=["recordings"])
logger = logging.getLogger(__name__)


@router.post("/", status_code=201, response_model=S3RecordingSchema)
async def load_recording(upload_file: UploadFile, s3_client=Depends(get_s3_client), settings=Depends(get_settings)):
    try:
        await validate_file(upload_file)
    except FileValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))

    recording_id = f'{uuid4()}-{upload_file.filename}'
    try:
        s3_client.upload_fileobj(upload_file.file, settings.S3_BUCKET, recording_id)
    except ClientError as e:
        logger.error(f'Failed to upload recording to S3\n{e.response["Error"]}')
        raise HTTPException(status_code=500, detail='File upload failed')

    return {'recording_id': recording_id}
