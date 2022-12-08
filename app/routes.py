import logging
from uuid import uuid4

from botocore.exceptions import ClientError
from fastapi import APIRouter, Depends, HTTPException, UploadFile

from app.dependencies import get_s3_bucket
from app.file_validation import FileValidationError, validate_file
from app.schemas import S3RecordingSchema

router = APIRouter(prefix="/recordings", tags=["recordings"])
logger = logging.getLogger(__name__)


@router.post("/", status_code=201, response_model=S3RecordingSchema)
async def load_recording(upload_file: UploadFile, s3_bucket=Depends(get_s3_bucket)):
    try:
        await validate_file(upload_file)
    except FileValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))

    recording_id = f'{uuid4()}-{upload_file.filename}'
    try:
        s3_bucket.upload_fileobj(upload_file.file, recording_id)
    except ClientError as e:
        logger.error(f'Failed to upload recording to S3\n{e.response["Error"]}')
        raise HTTPException(status_code=500, detail='File upload failed')

    return {'recording_id': recording_id}


@router.get("/", status_code=200, response_model=list[S3RecordingSchema])
async def get_all_recordings(s3_bucket=Depends(get_s3_bucket)):
    try:
        summaries = s3_bucket.objects.all()
    except ClientError as e:
        logger.error(f'Failed to get recordings from S3\n{e.response["Error"]}')
        raise HTTPException(status_code=500, detail='Failed to get recordings from S3')

    recordings = [S3RecordingSchema(recording_id=summary.key) for summary in summaries]
    return recordings
