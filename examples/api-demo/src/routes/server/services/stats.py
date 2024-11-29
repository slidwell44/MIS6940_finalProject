import asyncio
import logging
import psutil
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class Stats(BaseModel):
    cpu_usage: str = Field(..., description="The CPU usage percentage as a string.")
    memory_usage: str = Field(..., description="The memory usage percentage as a string.")
    total_memory: str = Field(..., description="The total memory available on the system in GB.")
    available_memory: str = Field(..., description="The available memory on the system in GB.")
    used_memory: str = Field(..., description="The used memory on the system in GB.")

    @classmethod
    async def get_stats(cls) -> "Stats":
        try:
            logger.debug("Starting to gather system stats.")

            cpu_usage = await asyncio.to_thread(psutil.cpu_percent, interval=1)
            memory = await asyncio.to_thread(psutil.virtual_memory)
            memory_usage = memory.percent

            stats = cls(
                cpu_usage=f"{cpu_usage}%",
                memory_usage=f"{memory_usage}%",
                total_memory=f"{memory.total / (1024 ** 3):.2f} GB",
                available_memory=f"{memory.available / (1024 ** 3):.2f} GB",
                used_memory=f"{memory.used / (1024 ** 3):.2f} GB"
            )

            logger.info(f"Payload returned: {stats.model_dump_json()}")

            return stats
        except Exception as e:
            logger.error(f"Error retrieving system stats: {e}", exc_info=True)
            raise
