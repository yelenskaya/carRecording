from uuid import UUID

from pydantic import BaseModel, Extra


class LocationSchema(BaseModel):
    lat: float
    long: float


class SpeedSchema(BaseModel):
    value: float
    unit: str


class FuelConsumptionSchema(BaseModel):
    amount: float
    unit: str


class CarSignalSchema(BaseModel):
    speed: SpeedSchema | None = None
    steering_angle: float | None = None
    location: LocationSchema | None = None
    fuel_consumption: FuelConsumptionSchema | None = None
    abs: bool | None = None
    ambient_temperature: float | None = None
    idle_time: float | None = None
    load: float | None = None

    class Config:
        extra = Extra.forbid


class RecordSchema(BaseModel):
    timestamp: int
    data: CarSignalSchema

    class Config:
        extra = Extra.forbid


class S3RecordingSchema(BaseModel):
    recording_id: UUID


class Notification(BaseModel):
    message: str
