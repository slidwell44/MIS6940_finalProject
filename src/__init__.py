import logging

from fastapi import FastAPI

logger = logging.getLogger()
logger.setLevel(logging.INFO)

stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.DEBUG)
stream_formatter = logging.Formatter('%(asctime)s | %(name)s | %(levelname)s | %(message)s')
stream_handler.setFormatter(stream_formatter)
logger.addHandler(stream_handler)

app = FastAPI(
    title="Project Seminar API",
    description="Simon Lidwell's final project API to do stuff"
)

__all__ = ['app', 'logger']
