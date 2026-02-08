from fastapi import APIRouter, Depends, HTTPException, status, Request, Response, Cookie
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import timedelta, datetime, timezone
from typing import Optional
import secrets

from . import schemas, crud, security
from .dependencies import get_db, get_current_user


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=schemas.UserOut)
async def register(user_in: schemas.UserCreate, db: AsyncSession = Depends(get_db)):
  existing = await crud.get_user_by_username(db, user_in.username)
  if existing:
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already registered")
  user = await crud.create_user(db, username=user_in.username, password=user_in.password, email=user_in.email)
  return user


@router.post("/token", response_model=schemas.Token)
async def login_for_access_token(
  request: Request,
  response: Response,
  form_data: OAuth2PasswordRequestForm = Depends(),
  db: AsyncSession = Depends(get_db),
) -> schemas.Token:
  try:
    user = await crud.get_user_by_username(db, form_data.username)
    if not user or not security.verify_password(form_data.password, user.hashed_password):
      raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect username or password",
        headers={"WWW-Authenticate": "Bearer"},
      )
  except HTTPException:
    raise
  except Exception as e:
    print(f"Error logging in: {e}")
    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error logging in")

  access_expires = timedelta(minutes=security.ACCESS_TOKEN_EXPIRE_MINUTES)
  access_token = security.create_access_token(subject=user.username, expires_delta=access_expires)

  jti = secrets.token_urlsafe(16)
  refresh_expires = timedelta(minutes=security.REFRESH_TOKEN_EXPIRE_MINUTES)
  refresh_token = security.create_refresh_token(jti=jti, subject=user.username, expires_delta=refresh_expires)

  expires_at = datetime.now(timezone.utc) + refresh_expires
  await crud.create_refresh_token(db=db, user_id=user.id, jti=jti, token_str=refresh_token, expires_at=expires_at)

  response.set_cookie(
    key="refresh_token",
    value=refresh_token,
    httponly=True,
    secure=request.url.scheme == "https",
    samesite="lax",
    max_age=int(refresh_expires.total_seconds()),
  )

  return schemas.Token(access_token=access_token, token_type="bearer")


@router.post("/refresh", response_model=schemas.Token)
async def refresh_access_token(
  refresh_token: Optional[str] = Cookie(None, alias="refresh_token"),
  db: AsyncSession = Depends(get_db),
) -> schemas.Token:
  if not refresh_token:
    raise HTTPException(
      status_code=status.HTTP_401_UNAUTHORIZED,
      detail="Refresh token missing",
      headers={"WWW-Authenticate": "Bearer"},
    )
  payload = security.decode_token(refresh_token)
  if not payload or payload.get("jti") is None or payload.get("sub") is None:
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

  jti = payload["jti"]
  username = payload["sub"]
  rt = await crud.get_refresh_token_by_jti(db, jti)
  if not rt or rt.expires_at < datetime.now(timezone.utc):
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token expired or revoked")

  user = await crud.get_user_by_username(db, username)
  if not user or user.disabled:
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found or disabled")

  access_expires = timedelta(minutes=security.ACCESS_TOKEN_EXPIRE_MINUTES)
  access_token = security.create_access_token(subject=user.username, expires_delta=access_expires)

  return schemas.Token(access_token=access_token, token_type="bearer")


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
  response: Response,
  refresh_token: Optional[str] = Cookie(None, alias="refresh_token"),
  db: AsyncSession = Depends(get_db),
):
  if refresh_token:
    payload = security.decode_token(refresh_token)
    if payload and payload.get("jti"):
      await crud.revoke_refresh_token(db, payload["jti"])
  response.delete_cookie(key="refresh_token")
  return None


@router.get("/me", response_model=schemas.UserOut)
async def get_me(current_user=Depends(get_current_user)):
  return current_user