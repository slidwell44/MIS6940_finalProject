from sqlalchemy import Column, Integer, Float, DateTime
from .base import Base
from datetime import datetime, UTC


class WimesprodsrvSystemStats(Base):
    __tablename__ = "wimesprodsrv_system_stats"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.now(UTC))
    cpu_usage = Column(Float)
    memory_usage = Column(Float)
    total_memory = Column(Float)
    available_memory = Column(Float)
    used_memory = Column(Float)
