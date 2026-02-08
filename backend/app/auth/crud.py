from typing import Optional
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import NoResultFound
from datetime import datetime
import hashlib


from . import models
from .security import get_password_hash


async def get_user_by_username(db: AsyncSession, username: str):
  q = select(models.User).where(models.User.username == username)
  result = await db.execute(q)
  return result.scalar_one_or_none()


async def create_user(db: AsyncSession, username: str, password: str, email: Optional[str] = None):
  hashed = get_password_hash(password)
  user = models.User(username=username, hashed_password=hashed, email=email)
  db.add(user)
  await db.commit()
  await db.refresh(user)
  return user


async def create_refresh_token(db: AsyncSession, user_id: int, jti: str, token_str: str, expires_at: datetime):
  hashed = hashlib.sha256(token_str.encode()).hexdigest()
  rt = models.RefreshToken(user_id=user_id, jti=jti, hashed_token=hashed, expires_at=expires_at)
  db.add(rt)
  await db.commit()
  await db.refresh(rt)
  return rt


async def get_refresh_token_by_jti(db: AsyncSession, jti: str):
  q = select(models.RefreshToken).where(models.RefreshToken.jti == jti)
  result = await db.execute(q)
  return result.scalar_one_or_none()


async def revoke_refresh_token(db: AsyncSession, jti: str):
  q = delete(models.RefreshToken).where(models.RefreshToken.jti == jti)
  await db.execute(q)
  await db.commit()