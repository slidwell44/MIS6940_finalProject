from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
from pathlib import Path

from src.middlewares import (
    log_requests, DbLogHandler, FilterDebugMessages
)
from src.tasks import lifespan

# Determine the project's base directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Define the log file path
DEBUG_LOG_PATH = BASE_DIR / 'src' / 'debug.log'

# Ensure the log directory exists
DEBUG_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)

# Configure logging
# TODO: Use env variables to set logging level
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

# Avoid adding multiple handlers during reload
if not any(isinstance(handler, DbLogHandler) for handler in logger.handlers):
    # Debug File Handler
    debug_handler = logging.FileHandler(str(DEBUG_LOG_PATH))
    debug_handler.setLevel(logging.DEBUG)
    debug_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    debug_handler.setFormatter(debug_formatter)
    debug_filter = FilterDebugMessages()
    debug_handler.addFilter(debug_filter)
    logger.addHandler(debug_handler)

    # Database Handler
    db_log_handler = DbLogHandler()
    db_log_handler.setLevel(logging.INFO)
    db_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    db_log_handler.setFormatter(db_formatter)
    logger.addHandler(db_log_handler)

    # # Optional: StreamHandler for console output (useful for debugging)
    # stream_handler = logging.StreamHandler()
    # stream_handler.setLevel(logging.DEBUG)
    # stream_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    # stream_handler.setFormatter(stream_formatter)
    # logger.addHandler(stream_handler)

# Create FastAPI app instance
app = FastAPI(
    lifespan=lifespan,
    title="EngineeringServicesApi",
    description="API for engineering services, including PDF overlay and server management",
)

# Configure middleware
# TODO: Set up authentication
app.middleware("http")(log_requests)
# noinspection PyTypeChecker
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Export app so it can be imported in main.py
__all__ = ["app", "logger"]
