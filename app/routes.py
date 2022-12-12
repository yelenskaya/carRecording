from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException, UploadFile
from starlette.background import BackgroundTasks

from app.background_tasks import reproduce_recording
from app.dependencies import get_s3_resource, get_settings
from app.file_validation import FileValidationError, validate_file
from app.s3_manager import get_all_object_summaries, get_file_object, S3Error, S3FileNotFoundError, upload_file_object
from app.schemas import Notification, S3RecordingSchema

router = APIRouter(prefix='/recordings', tags=['recordings'])


@router.post('/', status_code=201, response_model=S3RecordingSchema)
async def load_recording(upload_file: UploadFile, s3=Depends(get_s3_resource), settings=Depends(get_settings)):
    try:
        await validate_file(upload_file)
    except FileValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))

    recording_id = uuid4()

    recording_path = f'{recording_id}/record.csv'
    try:
        upload_file_object(s3, settings.S3_BUCKET, upload_file.file, recording_path)
    except S3Error:
        raise HTTPException(status_code=500, detail='File upload failed')

    return {'recording_id': recording_id}


@router.get('/', status_code=200, response_model=list[S3RecordingSchema])
async def get_all_recordings(s3=Depends(get_s3_resource), settings=Depends(get_settings)):
    try:
        summaries = get_all_object_summaries(s3, settings.S3_BUCKET)
    except S3Error:
        raise HTTPException(status_code=500, detail='Failed to get recordings from S3')

    recordings = [S3RecordingSchema(recording_id=summary.key.split('/')[0]) for summary in summaries]
    return recordings


@router.get('/reproduce/{recording_id}', status_code=202, response_model=Notification)
async def trigger_reproduction(
        recording_id: UUID,
        background_tasks: BackgroundTasks,
        s3=Depends(get_s3_resource),
        settings=Depends(get_settings)
):
    try:
        file = get_file_object(s3, settings.S3_BUCKET, f'{recording_id}/record.csv')
    except S3FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except S3Error:
        raise HTTPException(status_code=500, detail='Failed to get the file from S3')

    background_tasks.add_task(reproduce_recording, str(recording_id), file)

    return {'message': 'Recording started'}
