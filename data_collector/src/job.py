from datetime import datetime
from flask import request

from src.logger import logger
from src.main import collect_historical_data_for_all, collect_social_data_for_all, COINS
from src.sesison import init_session

def job():
    """
    Основная задача: сбор данных и отправка
    """
    logger.info(f"[{datetime.utcnow()}] Запуск сбора данных...")

    try:
        historical = collect_historical_data_for_all(list(COINS.keys()))
        posts = collect_social_data_for_all(list(COINS.keys()))
    except Exception as e:
        logger.info(f"[{datetime.utcnow()}] Ошибка в процессе сбора данных: {e}")
        
    init_session()
    try:
        post_payload = {"posts": posts}
        r = request.post(f"http://localhost:5001/process-data", json=post_payload)
        r.raise_for_status()
        logger.info(f"[{datetime.utcnow()}] Посты успешно отправлены ({len(posts)} шт.)")
    except Exception as e:
        logger.info(f"[{datetime.utcnow()}] Ошибка отправки постов: {e}")

    try:
        hist_payload = {"data": historical}
        r = request.post(f"http://localhost:5001/upload-historical-data", json=hist_payload)
        r.raise_for_status()
        logger.info(f"[{datetime.utcnow()}] Исторические данные успешно отправлены ({len(historical)} шт.)")
    except Exception as e:
        logger.info(f"[{datetime.utcnow()}] Ошибка отправки исторических данных: {e}")