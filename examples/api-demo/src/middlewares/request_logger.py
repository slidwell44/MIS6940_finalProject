from fastapi import Request, Response
from src.db import get_dev_db
from src.db.models.request_log import RequestLog
import time
from datetime import datetime, UTC


async def log_requests(request: Request, call_next) -> Response:
    start_time = time.time()
    response: Response = await call_next(request)
    process_time = time.time() - start_time

    db = next(get_dev_db())

    try:
        log = RequestLog(
            ip_address=request.client.host,
            method=request.method,
            url=str(request.url),
            request_time=datetime.now(UTC),
            response_time=datetime.now(UTC),
            duration=int(process_time * 1000),
            response_status=response.status_code
        )
        db.add(log)
        db.commit()
    finally:
        db.close()

    return response
