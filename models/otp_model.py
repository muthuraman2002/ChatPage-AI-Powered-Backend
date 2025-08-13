from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from .db import Base

class OTPLog(Base):
    __tablename__ = "otp_logs"

    id = Column(Integer, primary_key=True, index=True)
    phone = Column(String, index=True)
    otp = Column(String)
    status = Column(String)  # e.g., sent, verified, failed
    created_at = Column(DateTime, default=datetime.utcnow)
