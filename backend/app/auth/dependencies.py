from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from . import crud
from . import models
from .security import decode_token
from .db import AsyncSessionLocal

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")


async def get_db():
  async with AsyncSessionLocal() as session:
    yield session


async def get_current_user(
  token: str = Depends(oauth2_scheme),
  db: AsyncSession = Depends(get_db),
) -> models.User:
  credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
  )
  payload = decode_token(token)
  if payload is None:
    raise credentials_exception
  username: str = payload.get("sub")
  if username is None:
    raise credentials_exception

  user = await crud.get_user_by_username(db, username)
  if user is None:
    raise credentials_exception
  if user.disabled:
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Inactive user")
  return user
