from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from database import Base
import datetime

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    phone = Column(String(255), nullable=False)
    emergency_contact = Column(String(255), nullable=True)
    emergency_enabled = Column(Boolean, default=False)

class Medicine(Base):
    __tablename__ = "medicines"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    name = Column(String(255), nullable=False)
    time = Column(String(255), nullable=False)
    notified = Column(Boolean, default=False)

class SOS(Base):
    __tablename__ = "sos"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    emergency_number = Column(String(255), nullable=False)
    status = Column(Boolean, default=False)
