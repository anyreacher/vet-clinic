import os
from datetime import datetime, timedelta, timezone
from typing import Optional
import secrets
from jose import jwt, JWTError
from passlib.context import CryptContext


SECRET_KEY = os.getenv("SECRET_KEY") or secrets.token_urlsafe(32)
ALGORITHM = os.getenv("ALGORITHM") or "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "15"))
REFRESH_TOKEN_EXPIRE_MINUTES = int(os.getenv("REFRESH_TOKEN_EXPIRE_MINUTES", str(60 * 24 * 7)))

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password: str) -> str:
  return pwd_context.hash(password)




def verify_password(plain_password: str, hashed_password: str) -> bool:
  return pwd_context.verify(plain_password, hashed_password)




def create_access_token(*, subject: str, expires_delta: Optional[timedelta] = None, additional_claims: Optional[dict] = None) -> str:
  now = datetime.now(timezone.utc)
  if expires_delta:
    expire = now + expires_delta
  else:
    expire = now + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)


  payload = {"sub": subject, "iat": now, "exp": expire}
  if additional_claims:
    payload.update(additional_claims)
  token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
  
  return token


def create_refresh_token(*, jti: str, subject: str, expires_delta: Optional[timedelta] = None) -> str:
  now = datetime.now(timezone.utc)
  if expires_delta:
    expire = now + expires_delta
  else:
    expire = now + timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES)
  payload = {"sub": subject, "iat": now, "exp": expire, "jti": jti}
  token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
  return token


def decode_token(token: str) -> Optional[dict]:
  try:
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
  except JWTError:
    return None