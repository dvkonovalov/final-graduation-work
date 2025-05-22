from datetime import datetime
from flask import jsonify

from src.logger import logger
from src.main import collect_historical_data_for_all, collect_social_data_for_all, COINS
from src.sesison import init_session, proxy

def job():
    """
    Основная задача: сбор данных и отправка
    """
    logger.debug(f"[{datetime.utcnow()}] Запуск сбора данных...")
    jti = init_session()
    if not jti:
        return jsonify({'result' : 400})
    

    try:
        historical = collect_historical_data_for_all(list(COINS.keys()))
        posts = collect_social_data_for_all(list(COINS.keys()))
    except Exception as e:
        logger.debug(f"[{datetime.utcnow()}] Ошибка в процессе сбора данных: {e}")

    try:
        post_payload = {"posts": posts}
        r = proxy(
            jti=jti,
            path="http://preparing:5002/process-data",
            data=post_payload
        )
        r.raise_for_status()
        logger.debug(f"[{datetime.utcnow()}] Посты успешно отправлены ({len(posts)} шт.)")
    except Exception as e:
        logger.debug(f"[{datetime.utcnow()}] Ошибка отправки постов: {e}")

    try:
        hist_payload = {"data": historical}
        r = proxy(
            jti=jti,
            path="http://preparing:5002/upload-historical-data",
            data=hist_payload
        )
        r.raise_for_status()
        logger.debug(f"[{datetime.utcnow()}] Исторические данные успешно отправлены ({len(historical)} шт.)")
    except Exception as e:
        logger.debug(f"[{datetime.utcnow()}] Ошибка отправки исторических данных: {e}")
    
    return jsonify({'result' : 200})