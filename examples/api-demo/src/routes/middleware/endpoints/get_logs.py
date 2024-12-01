from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime

from src.db import get_dev_db
from src.db.models.request_log import RequestLog

app = FastAPI()


@app.get("/logs/")
def get_logs(
        skip: int = 0,
        limit: int = 10,
        ip_address: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        db: Session = Depends(get_dev_db),
):
    query = db.query(RequestLog)

    if ip_address:
        query = query.filter(RequestLog.ip_address == ip_address)
    if start_date:
        query = query.filter(RequestLog.request_time >= start_date)
    if end_date:
        query = query.filter(RequestLog.request_time <= end_date)

    logs = query.offset(skip).limit(limit).all()
    return logs
