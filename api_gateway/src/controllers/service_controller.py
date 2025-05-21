from flask import request
from src.logger import logger

def init_session():
    values = request.get_json()
    logger.info(values)
    pass