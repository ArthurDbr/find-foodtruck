import re

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator, model_validator

_TIME_RE = re.compile(r"^([01]\d|2[0-3]):[0-5]\d$")


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    email: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut


class StopBase(BaseModel):
    day_of_week: int = Field(ge=0, le=6, description="0 = Monday ... 6 = Sunday")
    start_time: str = Field(examples=["11:30"])
    end_time: str = Field(examples=["14:30"])
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    address: str = Field(default="", max_length=255)
    note: str = Field(default="", max_length=255)

    @field_validator("start_time", "end_time")
    @classmethod
    def _check_time(cls, v: str) -> str:
        if not _TIME_RE.match(v):
            raise ValueError("time must be HH:MM (24h)")
        return v

    @model_validator(mode="after")
    def _check_order(self):
        if self.end_time <= self.start_time:
            raise ValueError("end_time must be after start_time")
        return self


class StopCreate(StopBase):
    pass


class StopOut(StopBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    truck_id: int


class TruckBase(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    cuisine: str = Field(default="", max_length=80)
    description: str = Field(default="", max_length=2000)


class TruckCreate(TruckBase):
    pass


class TruckOut(TruckBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    owner_id: int
    stops: list[StopOut] = []


class TruckSummary(TruckBase):
    model_config = ConfigDict(from_attributes=True)
    id: int


class StopWithTruck(StopOut):
    truck: TruckSummary
    distance_km: float | None = None


class GeocodeResult(BaseModel):
    display_name: str
    latitude: float
    longitude: float
