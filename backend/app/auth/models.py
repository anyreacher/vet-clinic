from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, func, Text
from sqlalchemy.orm import relationship
from .db import Base


class User(Base):
  __tablename__ = "users"
  id = Column(Integer, primary_key=True, index=True)
  username = Column(String(150), unique=True, index=True, nullable=False)
  email = Column(String(320), unique=True, index=True, nullable=True)
  hashed_password = Column(String, nullable=False)
  disabled = Column(Boolean, default=False)
  created_at = Column(DateTime(timezone=True), server_default=func.now())
  refresh_tokens = relationship("RefreshToken", back_populates="user", cascade="all, delete-orphan")


class RefreshToken(Base):
  __tablename__ = "refresh_tokens"
  id = Column(Integer, primary_key=True, index=True)
  user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
  jti = Column(String(255), unique=True, nullable=False, index=True)
  hashed_token = Column(Text, nullable=False)
  expires_at = Column(DateTime(timezone=True), nullable=False)
  created_at = Column(DateTime(timezone=True), server_default=func.now())
  user = relationship("User", back_populates="refresh_tokens")


class Doctor(Base):
  __tablename__ = "doctors"
  id = Column(Integer, primary_key=True, index=True)
  name = Column(String(150), nullable=False)
  specialty = Column(String(150), nullable=True)
  appointments = relationship("Appointment", back_populates="doctor", cascade="all, delete-orphan")


class Appointment(Base):
  __tablename__ = "appointments"
  id = Column(Integer, primary_key=True, index=True)
  doctor_id = Column(Integer, ForeignKey("doctors.id", ondelete="CASCADE"), nullable=False)
  user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
  start_time = Column(DateTime(timezone=True), nullable=False)
  doctor = relationship("Doctor", back_populates="appointments")
  user = relationship("User", back_populates="appointments")


User.appointments = relationship("Appointment", back_populates="user", cascade="all, delete-orphan")