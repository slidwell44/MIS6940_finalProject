import logging
from datetime import datetime, UTC
from src.db import get_dev_db
from src.db.models import MessageLog
from concurrent.futures import ThreadPoolExecutor
import asyncio

logger = logging.getLogger(__name__)

executor = ThreadPoolExecutor()


class DbLogHandler(logging.Handler):
    def __init__(self):
        super().__init__()

    def emit(self, record):
        """
        This method is called by the Python logging library to handle a log message.
        Since the logging library expects this method to be synchronous,
        use asyncio to schedule the async handling
        """
        try:
            loop = asyncio.get_event_loop()

            if loop.is_running():
                # If we are in a running event loop, create an async task
                loop.create_task(self.async_emit(record))
            else:
                # If no event loop is running, manually get the event loop and run it
                loop.run_until_complete(self.async_emit(record))
        except Exception as e:
            logger.debug(f"Something broke: {e}", exc_info=True)

    async def async_emit(self, record):
        """
        Async method to emit log messages to the database
        """
        log_entry = self.format(record)
        level = record.levelname

        def sync_db_task():
            try:
                with next(get_dev_db()) as session:
                    log_message = MessageLog(
                        level=level,
                        message=log_entry,
                        timestamp=datetime.now(UTC),
                        logger_name=logger.name,
                        function_name=record.funcName,
                        line_number=record.lineno,
                        exception_info=record.exc_info,
                    )

                    session.add(log_message)
                    session.commit()
            except Exception as e:
                logger.debug(f"Something broke: {e}", exc_info=True)

        # Run the synchronous task in a thread pool to avoid blocking the event loop
        await asyncio.get_running_loop().run_in_executor(executor, sync_db_task)
