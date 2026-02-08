from datetime import datetime, timedelta, timezone
from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_db, get_current_user
from app.auth import models
from app.appointments import crud, schemas

router = APIRouter(prefix="/appointments", tags=["appointments"])


@router.get("/doctors", response_model=List[schemas.DoctorOut])
async def list_doctors(db: AsyncSession = Depends(get_db)):
  doctors = await crud.get_doctors(db)
  return doctors


@router.get("/slots", response_model=schemas.SlotsResponse)
async def get_slots(
  doctor_id: int,
  week_start: Optional[str] = None,
  db: AsyncSession = Depends(get_db),
):
  doctor = await crud.get_doctor_by_id(db, doctor_id)
  if not doctor:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Doctor not found")

  if week_start:
    try:
      start_dt = datetime.fromisoformat(week_start.replace("Z", "+00:00"))
    except ValueError:
      raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid week_start (use ISO date)")
  else:
    today = datetime.now(timezone.utc).date()
    monday = today - timedelta(days=today.weekday())
    start_dt = datetime.combine(monday, datetime.min.time(), tzinfo=timezone.utc)

  if start_dt.tzinfo is None:
    start_dt = start_dt.replace(tzinfo=timezone.utc)

  slots = await crud.get_slots_for_week(db, doctor_id=doctor_id, week_start=start_dt)
  return schemas.SlotsResponse(
    slots=[
      schemas.SlotOut(start=s, end=e, booked=booked)
      for s, e, booked in slots
    ]
  )


@router.post("", response_model=schemas.AppointmentOut, status_code=status.HTTP_201_CREATED)
async def book_appointment(
  body: schemas.AppointmentCreate,
  db: AsyncSession = Depends(get_db),
  current_user: models.User = Depends(get_current_user),
):
  doctor = await crud.get_doctor_by_id(db, body.doctor_id)
  if not doctor:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Doctor not found")

  start_time = body.start_time
  if start_time.tzinfo is None:
    start_time = start_time.replace(tzinfo=timezone.utc)
  if start_time < datetime.now(timezone.utc):
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot book in the past")

  week_start = start_time.replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=start_time.weekday())
  slots = await crud.get_slots_for_week(db, doctor_id=body.doctor_id, week_start=week_start)
  start_utc = start_time
  for s, e, booked in slots:
    if abs((s - start_utc).total_seconds()) < 60:
      if booked:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Slot already booked")
      break
  else:
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or outside working hours")

  appointment = await crud.create_appointment(
    db, doctor_id=body.doctor_id, user_id=current_user.id, start_time=start_time
  )
  return appointment
