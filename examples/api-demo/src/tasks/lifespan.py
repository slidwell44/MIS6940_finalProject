import asyncio
from asyncio import Task
from contextlib import asynccontextmanager
from fastapi import FastAPI
import logging
from typing import Optional, AsyncGenerator

from src.db import Base
from src.db.servers.widevdbsrv import get_engine
from src.tasks import periodic_collect_and_store_system_stats

logger = logging.getLogger(__name__)

background_task: Optional[Task] = None


# noinspection PyUnusedLocal
@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    global background_task

    try:
        # Startup logic
        from src.tasks import get_parent_release_branch

        version = get_parent_release_branch()
        app.version = version
        logger.info(f"Set application version to {version}")

        engine = get_engine().engine
        with engine.begin() as conn:
            Base.metadata.create_all(bind=conn)
        logger.debug("Database tables created successfully.")

        # Start the background task to log system stats
        background_task = asyncio.create_task(periodic_collect_and_store_system_stats())
        logger.debug("Background Task: Started periodic_collect_and_store_system_stats.")

        yield

    finally:
        # Shutdown logic
        if background_task:
            logger.debug("Background Task: Cancelling periodic_collect_and_store_system_stats.")
            background_task.cancel()
            try:
                await background_task
            except asyncio.CancelledError:
                logger.debug("Background Task: Successfully cancelled.")
            except Exception as e:
                logger.error(f"Background Task: Error during cancellation: {e}", exc_info=True)
