import asyncio
from concurrent.futures import ThreadPoolExecutor
import logging
import psutil

from src.db.models import WimesprodsrvSystemStats
from src.db import get_dev_db

logger = logging.getLogger(__name__)

executor = ThreadPoolExecutor()


def collect_and_store_system_stats():
    try:
        cpu_usage = psutil.cpu_percent(interval=None)
        memory = psutil.virtual_memory()

        with next(get_dev_db()) as session:

            stats = WimesprodsrvSystemStats(
                cpu_usage=cpu_usage,
                memory_usage=memory.percent,
                total_memory=memory.total / (1024 ** 3),
                available_memory=memory.available / (1024 ** 3),
                used_memory=memory.used / (1024 ** 3),
            )
            session.add(stats)
            session.commit()

        logger.debug("System stats collected and stored successfully.")

    except Exception as e:
        logger.error(f"Error retrieving or storing system stats: {e}", exc_info=True)


async def periodic_collect_and_store_system_stats():
    while True:
        try:
            logger.debug("Background Task: Attempting to collect system stats.")
            await asyncio.get_running_loop().run_in_executor(executor, collect_and_store_system_stats)
            logger.debug("Background Task: Successfully collected and stored system stats.")
        except Exception as e:
            logger.error(f"Background Task: Unexpected error: {e}", exc_info=True)
        await asyncio.sleep(5)
