# app/models/user.py
from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from ..core.datebase import Base

class EnterpriseUser(Base):
    __tablename__ = "enterprise_users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    company_name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    avatar = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)