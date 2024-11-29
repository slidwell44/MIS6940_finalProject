from sqlalchemy import Column, Integer, String, DateTime, Numeric
from .base import Base


class RequestLog(Base):
    __tablename__ = "request_logs"

    id = Column(Integer, primary_key=True, index=True)
    ip_address = Column(String(50), index=True)
    method = Column(String(10))
    url = Column(String(200))
    request_time = Column(DateTime)
    response_time = Column(DateTime)
    duration = Column(Numeric(precision=10, scale=2))
    response_status = Column(Integer)
