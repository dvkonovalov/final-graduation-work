from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime

from src import create_app, CONFIG
from src.job import job
from src.logger import logger


app = create_app()
app.app_context().push()

scheduler = BackgroundScheduler()
scheduler.add_job(func=job, trigger="interval", hours=CONFIG['collection_interval_hours'])

logger.info(f"[{datetime.utcnow()}] Data Collector запущен. Сбор каждые {CONFIG['collection_interval_hours']} часов.")

scheduler.start()


if __name__ == "__main__":
    try:
        app.run(debug=True)
    except KeyboardInterrupt:
        pass
    finally:
        scheduler.shutdown()
        
        # !!!!!!!!!! ПАРОЛЬ от КЛЮЧА #  TODO:: b'dba21ddc-665d-40e5-8f54-8fbae6c40192'