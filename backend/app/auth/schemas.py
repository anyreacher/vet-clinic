from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class UserCreate(BaseModel):
  username: str
  password: str
  email: Optional[EmailStr] = None


class UserOut(BaseModel):
  id: int
  username: str
  email: Optional[EmailStr] = None
  disabled: bool
  created_at: datetime

  model_config = {"from_attributes": True}


class Token(BaseModel):
  access_token: str
  token_type: str


class TokenPayload(BaseModel):
  sub: str
  exp: int
  jti: Optional[str] = None