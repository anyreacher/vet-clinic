from datetime import datetime, time, timedelta, timezone
from typing import List, Tuple

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import models

# Working hours: 9:00 - 17:00, 30-minute slots
SLOT_DURATION_MINUTES = 30
WORK_START = time(9, 0)
WORK_END = time(17, 0)


async def get_doctors(db: AsyncSession) -> List[models.Doctor]:
  result = await db.execute(select(models.Doctor).order_by(models.Doctor.name))
  return list(result.scalars().all())


async def ensure_doctors_seed(db: AsyncSession) -> None:
  result = await db.execute(select(func.count()).select_from(models.Doctor))
  if result.scalar() > 0:
    return
  for name, specialty in [
    ("Dr. Sarah Miller", "General practice"),
    ("Dr. James Chen", "Surgery"),
    ("Dr. Emma Wilson", "Dentistry"),
  ]:
    db.add(models.Doctor(name=name, specialty=specialty))
  await db.commit()


async def get_doctor_by_id(db: AsyncSession, doctor_id: int):
  result = await db.execute(select(models.Doctor).where(models.Doctor.id == doctor_id))
  return result.scalar_one_or_none()


def _week_slots(week_start: datetime) -> List[Tuple[datetime, datetime]]:
  """Generate (start, end) slot datetimes for Mon-Sun, work hours, 30 min."""
  slots = []
  for day_offset in range(7):
    day = week_start.date() + timedelta(days=day_offset)
    current = datetime.combine(day, WORK_START, tzinfo=timezone.utc)
    end_dt = datetime.combine(day, WORK_END, tzinfo=timezone.utc)
    while current < end_dt:
      slot_end = current + timedelta(minutes=SLOT_DURATION_MINUTES)
      slots.append((current, slot_end))
      current = slot_end
  return slots


async def get_slots_for_week(
  db: AsyncSession,
  doctor_id: int,
  week_start: datetime,
) -> List[Tuple[datetime, datetime, bool]]:
  """Return list of (start, end, booked) for the doctor in that week."""
  all_slots = _week_slots(week_start)
  week_end = week_start + timedelta(days=7)
  result = await db.execute(
    select(models.Appointment.start_time).where(
      models.Appointment.doctor_id == doctor_id,
      models.Appointment.start_time >= week_start,
      models.Appointment.start_time < week_end,
    )
  )
  booked_starts = set()
  for row in result.fetchall():
    t = row[0]
    if t.tzinfo is None:
      t = t.replace(tzinfo=timezone.utc)
    booked_starts.add(t)

  out = []
  for start, end in all_slots:
    start_utc = start if start.tzinfo else start.replace(tzinfo=timezone.utc)
    booked = any(abs((bs - start_utc).total_seconds()) < 60 for bs in booked_starts)
    out.append((start, end, booked))
  return out


async def create_appointment(
  db: AsyncSession,
  doctor_id: int,
  user_id: int,
  start_time: datetime,
) -> models.Appointment:
  apt = models.Appointment(doctor_id=doctor_id, user_id=user_id, start_time=start_time)
  db.add(apt)
  await db.commit()
  await db.refresh(apt)
  return apt
