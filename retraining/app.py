from src import create_app
from src.job import job
from src.logger import logger

from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler

app = create_app()

app.app_context().push()


scheduler = BackgroundScheduler()
scheduler.add_job(func=job, trigger="interval", hours=24)

logger.info(f"[{datetime.utcnow()}] Data Collector запущен. Сбор каждые {24} часa.")

scheduler.start()

if __name__ == "__main__":
    try:
        app.run(debug=True, host='0.0.0.0', port=5004)
    except KeyboardInterrupt:
        pass
    finally:
        scheduler.shutdown()