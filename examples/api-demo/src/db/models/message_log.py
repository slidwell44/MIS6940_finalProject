from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime
from typing import Optional

from .base import Base


class MessageLog(Base):
    __tablename__ = "message_log"

    id: int = Column(Integer, primary_key=True, index=True)
    level: str = Column(String, nullable=False)
    message: str = Column(String, nullable=False)
    timestamp: datetime = Column(
        DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )
    logger_name: Optional[str] = Column(String, nullable=True)
    function_name: Optional[str] = Column(String, nullable=True)
    line_number: Optional[int] = Column(Integer, nullable=True)
    exception_info: Optional[str] = Column(String, nullable=True)
