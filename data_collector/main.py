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

# Создаем папку для резервных копий, если её нет
os.makedirs(os.path.dirname(config['backup_paths']['posts']), exist_ok=True)
os.makedirs(os.path.dirname(config['backup_paths']['historical']), exist_ok=True)

# Адрес FastAPI сервера
FASTAPI_URL = config['fastapi_base_url']

# Монеты для сбора
COINS = {
    "bitcoin": "Bitcoin",
    "ethereum": "Ethereum",
    "litecoin": "Litecoin"
}

def save_backup(data: List[dict], base_path: str, mode: str):
    """
    Сохраняем данные в отдельные файлы по монетам
    """
    df = pd.DataFrame(data)
    if df.empty:
        print(f"[{datetime.utcnow()}] Нет данных для резервного копирования ({mode}).")
        return

    # Убедимся, что coin — строка
    df["coin"] = df["coin"].apply(lambda x: x[0] if isinstance(x, list) else x)

    if "coin" not in df.columns:
        print(f"[{datetime.utcnow()}] Ошибка: в данных нет столбца 'coin'.")
        return

    backup_dir = os.path.dirname(base_path)
    os.makedirs(backup_dir, exist_ok=True)

    for coin_id, coin_df in df.groupby("coin"):
        base_filename = f"backup_{mode}_{coin_id}.csv"
        backup_path = os.path.join(backup_dir, base_filename)

        if os.path.exists(backup_path):
            existing_df = pd.read_csv(backup_path)
            combined_df = pd.concat([existing_df, coin_df], ignore_index=True)
        else:
            combined_df = coin_df

        combined_df.drop_duplicates(inplace=True)
        combined_df.to_csv(backup_path, index=False)

        print(f"[{datetime.utcnow()}] Данные для {coin_id} сохранены в файл {backup_path} (всего {len(combined_df)} записей).")

def collect_historical_data(coin_id: str):
    """
    Сбор исторических данных для одной монеты и резервное копирование
    """
    headers = {
        "x-cg-demo-api-key": "CG-qmG711yyLriQUS8GE4RfSbed"
    }

    ohlc_url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/ohlc"
    params = {
        "vs_currency": "usd",
        "days": config.get('historical_days', 90)
    }
    ohlc_response = requests.get(ohlc_url, params=params, headers=headers)
    ohlc_response.raise_for_status()
    ohlc_data = ohlc_response.json()

    print(f"[{datetime.utcnow()}] Получены OHLC данные для {coin_id}")

    print(f"[{datetime.utcnow()}] Пауза 60 секунд перед запросом volumes для {coin_id}")
    time.sleep(60)

    volume_url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart"
    volume_params = {
        "vs_currency": "usd",
        "days": config.get('historical_days', 90)
    }
    volume_response = requests.get(volume_url, params=volume_params, headers=headers)
    volume_response.raise_for_status()
    volume_data = volume_response.json()

    volumes = volume_data.get('total_volumes', [])
    volume_dict = {int(ts): vol for ts, vol in volumes}

    records = []
    for ohlc in ohlc_data:
        timestamp_ms = int(ohlc[0])
        timestamp = datetime.utcfromtimestamp(timestamp_ms / 1000).isoformat()

        open_price = ohlc[1]
        high_price = ohlc[2]
        low_price = ohlc[3]
        close_price = ohlc[4]

        closest_volume = None
        closest_diff = float('inf')
        for v_ts, v in volume_dict.items():
            diff = abs(timestamp_ms - v_ts)
            if diff < closest_diff:
                closest_volume = v
                closest_diff = diff

        records.append({
            "coin": coin_id,
            "timestamp": timestamp,
            "open": open_price,
            "high": high_price,
            "low": low_price,
            "close": close_price,
            "volume": closest_volume
        })

    # Сохраняем сразу
    save_backup(records, config['backup_paths']['historical'], "historical")

    return records

def collect_historical_data_for_all(coins: List[str]):
    """
    Сбор исторических данных для всех монет
    """
    all_records = []

    for coin_id in coins:
        try:
            records = collect_historical_data(coin_id)
            all_records.extend(records)
        except Exception as e:
            print(f"[{datetime.utcnow()}] Ошибка при сборе исторических данных для {coin_id}: {e}")

        print(f"[{datetime.utcnow()}] Пауза 60 секунд перед следующей монетой...")
        time.sleep(60)

    return all_records

def collect_social_data(coin_id: str):
    """
    Сбор постов с Reddit по монете и резервное копирование
    """
    subreddit_name = COINS[coin_id]
    subreddit = reddit.subreddit(subreddit_name)

    time_threshold = datetime.utcnow() - timedelta(hours=config['collection_interval_hours'])
    posts = []
    for post in subreddit.new(limit=100):
        post_time = datetime.utcfromtimestamp(post.created_utc)
        if post_time > time_threshold:
            posts.append({
                "coin": coin_id,
                "text": post.title + " " + (post.selftext or ""),
                "timestamp": post_time.isoformat(),
                "hashtags": [tag.strip("#") for tag in post.title.split() if tag.startswith("#")]
            })

    # Сохраняем сразу
    save_backup(posts, config['backup_paths']['posts'], "posts")

    return posts

def collect_social_data_for_all(coins: List[str]):
    """
    Сбор постов для всех монет
    """
    all_posts = []

    for coin_id in coins:
        try:
            posts = collect_social_data(coin_id)
            all_posts.extend(posts)
        except Exception as e:
            print(f"[{datetime.utcnow()}] Ошибка при сборе постов для {coin_id}: {e}")

    return all_posts

def send_to_fastapi(posts: List[dict], historical: List[dict]):
    """
    Отправка данных на FastAPI сервер
    """
    try:
        post_payload = {"posts": posts}
        r = requests.post(f"{FASTAPI_URL}/process-data", json=post_payload)
        r.raise_for_status()
        print(f"[{datetime.utcnow()}] Посты успешно отправлены ({len(posts)} шт.)")
    except Exception as e:
        print(f"[{datetime.utcnow()}] Ошибка отправки постов: {e}")

    try:
        hist_payload = {"data": historical}
        r = requests.post(f"{FASTAPI_URL}/upload-historical-data", json=hist_payload)
        r.raise_for_status()
        print(f"[{datetime.utcnow()}] Исторические данные успешно отправлены ({len(historical)} шт.)")
    except Exception as e:
        print(f"[{datetime.utcnow()}] Ошибка отправки исторических данных: {e}")

def job():
    """
    Основная задача: сбор данных и отправка
    """
    print(f"[{datetime.utcnow()}] Запуск сбора данных...")

    try:
        historical = collect_historical_data_for_all(list(COINS.keys()))
        posts = collect_social_data_for_all(list(COINS.keys()))
        send_to_fastapi(posts, historical)
    except Exception as e:
        print(f"[{datetime.utcnow()}] Ошибка в процессе сбора данных: {e}")

def main():
    schedule.every(config['collection_interval_hours']).hours.do(job)

    print(f"[{datetime.utcnow()}] Data Collector запущен. Сбор каждые {config['collection_interval_hours']} часов.")

    # Первая задача сразу
    job()

    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    main()
