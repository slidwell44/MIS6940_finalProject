import threading
import logging

logger = logging.getLogger(__name__)


class SingletonMeta(type):
    _instances = {}
    _lock = threading.Lock()

    def __call__(cls, *args, **kwargs):
        logger.debug(f"SingletonMeta __call__ for {cls}")
        with cls._lock:
            if cls not in cls._instances:
                try:
                    logger.info(f"Creating new instance of {cls}")
                    cls._instances[cls] = super(SingletonMeta, cls).__call__(*args, **kwargs)
                    logger.debug(f"Instance created: {cls._instances[cls]}")
                except Exception as e:
                    logger.error(f"Error in SingletonMeta __call__ when creating instance of {cls}: {e}")
                    cls._instances[cls] = None
            else:
                logger.debug(f"Using existing instance of {cls}")
        return cls._instances[cls]
