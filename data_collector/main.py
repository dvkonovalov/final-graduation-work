import os
import yaml
import requests
import pandas as pd
import schedule
import time
from datetime import datetime, timedelta
import praw
from typing import List

# Загрузка конфигурации
with open("config.yaml", "r", encoding="utf-8") as f:
    config = yaml.safe_load(f)

# Инициализация Reddit клиента
reddit_config = config['reddit']
reddit = praw.Reddit(
    client_id=reddit_config['client_id'],
    client_secret=reddit_config['client_secret'],
    username=reddit_config['username'],
    password=reddit_config['password'],
    user_agent=reddit_config['user_agent']
)

# Создаем папку для резервных копий, если ее нет
os.makedirs(os.path.dirname(config['backup_paths']['posts']), exist_ok=True)

# Адрес FastAPI сервера
FASTAPI_URL = config['fastapi_base_url']


def collect_historical_data():
    """
    Получение исторических данных BTC с CoinGecko
    """
    url = "https://api.coingecko.com/api/v3/coins/bitcoin/market_chart"
    params = {
        "vs_currency": "usd",
        "days": "2"
    }

    headers = {
        "User-Agent": "CryptoDataCollectorBot/1.0",
        "x-cg-pro-api-key": "CG-qmG711yyLriQUS8GE4RfSbed"
    }

    response = requests.get(url, params=params, headers=headers)
    response.raise_for_status()
    data = response.json()

    records = []
    for price, volume in zip(data['prices'], data['total_volumes']):
        timestamp = datetime.utcfromtimestamp(price[0] / 1000).isoformat()
        price_value = price[1]
        volume_value = volume[1]

        records.append({
            "timestamp": timestamp,
            "open": price_value,  # Т.к. данных OHLC нет, повторяем цену
            "high": price_value,
            "low": price_value,
            "close": price_value,
            "volume": volume_value
        })

    return records


def collect_social_data():
    """
    Получение постов о Bitcoin с Reddit
    """
    subreddit = reddit.subreddit("Bitcoin")
    time_threshold = datetime.utcnow() - timedelta(minutes=config['collection_interval_minutes'])

    posts = []
    for post in subreddit.new(limit=100):
        post_time = datetime.utcfromtimestamp(post.created_utc)
        if post_time > time_threshold:
            posts.append({
                "text": post.title + " " + (post.selftext or ""),
                "timestamp": post_time.isoformat(),
                "hashtags": [tag.strip("#") for tag in post.title.split() if tag.startswith("#")]
            })

    return posts


def send_to_fastapi(posts: List[dict], historical: List[dict]):
    """
    Отправка данных на FastAPI сервер
    """
    post_payload = {"posts": posts}
    hist_payload = {"data": historical}

    # Отправка постов
    try:
        print(post_payload)
        r = requests.post(f"{FASTAPI_URL}/process-data", json=post_payload)
        r.raise_for_status()
        print(f"[{datetime.utcnow()}] Посты успешно отправлены ({len(posts)} шт.)")
    except Exception as e:
        print(f"[{datetime.utcnow()}] Ошибка отправки постов: {e}")
        save_backup(posts, config['backup_paths']['posts'], "posts")

    # Отправка исторических данных
    try:
        r = requests.post(f"{FASTAPI_URL}/upload-historical-data", json=hist_payload)
        r.raise_for_status()
        print(f"[{datetime.utcnow()}] Исторические данные успешно отправлены ({len(historical)} шт.)")
    except Exception as e:
        print(f"[{datetime.utcnow()}] Ошибка отправки исторических данных: {e}")
        save_backup(historical, config['backup_paths']['historical'], "historical")


def save_backup(data: List[dict], path: str, mode: str):
    """
    Сохраняет данные в файл при ошибке отправки
    """
    df = pd.DataFrame(data)
    if os.path.exists(path):
        existing_df = pd.read_csv(path)
        df = pd.concat([existing_df, df], ignore_index=True)
    df.to_csv(path, index=False)
    print(f"[{datetime.utcnow()}] Данные сохранены в резервный файл {path}")


def job():
    """
    Основная задача: сбор и отправка данных
    """
    print(f"[{datetime.utcnow()}] Запуск сбора данных...")
    try:
        historical = collect_historical_data()
        posts = collect_social_data()
        send_to_fastapi(posts, historical)
    except Exception as e:
        print(f"[{datetime.utcnow()}] Ошибка в процессе сбора данных: {e}")


def main():
    schedule.every(config['collection_interval_minutes']).minutes.do(job)

    print(f"[{datetime.utcnow()}] Data Collector запущен. Сбор каждые {config['collection_interval_minutes']} минут.")

    # Первая задача сразу при старте
    job()

    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == "__main__":
    main()
