from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel


class DoctorOut(BaseModel):
  id: int
  name: str
  specialty: Optional[str] = None

  model_config = {"from_attributes": True}


class SlotOut(BaseModel):
  start: datetime
  end: datetime
  booked: bool


class SlotsResponse(BaseModel):
  slots: List[SlotOut]


class AppointmentCreate(BaseModel):
  doctor_id: int
  start_time: datetime


class AppointmentOut(BaseModel):
  id: int
  doctor_id: int
  user_id: int
  start_time: datetime

  model_config = {"from_attributes": True}
