from fastapi import APIRouter, HTTPException
import logging
from typing import Dict

from src.routes.server.services import Stats

logger = logging.getLogger(__name__)

router = APIRouter(
    tags=["Wimesprodsrv"],
)


@router.get("/HealthCheck/", operation_id="health_check_server")
async def health_check() -> Dict:
    return {"message": "Hello World"}


@router.get("/SystemStats/", response_model=Stats, operation_id="system_stats_server")
async def system_stats() -> Stats:
    logger.debug("Received request for system stats.")
    try:
        stats = await Stats.get_stats()
        logger.debug("Successfully retrieved system stats.")
        return stats
    except Exception as e:
        logger.error(f"Failed to retrieve system stats: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to retrieve system stats.")


@router.post("/ThrowError/", operation_id="throw_error")
async def throw_error() -> None:
    raise HTTPException(status_code=404)
