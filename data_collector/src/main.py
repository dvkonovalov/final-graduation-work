import os
import requests
import pandas as pd
import time
from datetime import datetime, timedelta
import praw


from typing import List
from src.logger import logger
from src.db import db

CONFIG = {}

CONFIG['collection_interval_hours'] = os.environ.get('collection_interval_hours')
CONFIG['collection_interval_minutes'] = os.environ.get('collection_interval_minutes')

CONFIG['historical_days'] = os.environ.get('historical_days')

CONFIG['reddit'] = {}
CONFIG['reddit']['client_id'] = os.environ.get('reddit_client_id')
CONFIG['reddit']['client_secret'] = os.environ.get('reddit_client_secret')
CONFIG['reddit']['username'] = os.environ.get('reddit_username')
CONFIG['reddit']['password'] = os.environ.get('reddit_password')
CONFIG['reddit']['user_agent'] = os.environ.get('reddit_user_agent')

# Инициализация Reddit клиента
reddit_config = CONFIG['reddit']
reddit = praw.Reddit(
    client_id=reddit_config['client_id'],
    client_secret=reddit_config['client_secret'],
    username=reddit_config['username'],
    password=reddit_config['password'],
    user_agent=reddit_config['user_agent']
)

# Монеты для сбора
COINS = {
    "bitcoin": "Bitcoin",
    "ethereum": "Ethereum",
    "litecoin": "Litecoin"
}

def read_from_db(collection : str) -> pd.DataFrame:
    docs = list(db[collection].find())
    df_from_mongo = pd.DataFrame(docs)

    df_from_mongo.drop(columns=["_id"], inplace=True)
    return df_from_mongo

def check_collection_existance(collection : str) -> bool:
    return collection in db.list_collection_names()

def write_to_mongo(collection : str, df : pd.DataFrame) -> None:
    records = df.to_dict(orient="records")
    db[collection].delete_many({})
    db[collection].insert_many(records)

def save_backup(data: List[dict], mode: str):
    """
    Сохраняем данные в отдельные файлы по монетам
    """
    df = pd.DataFrame(data)
    if df.empty:
        logger.debug(f"[{datetime.utcnow()}] Нет данных для резервного копирования ({mode}).")
        return

    # Убедимся, что coin — строка
    df["coin"] = df["coin"].apply(lambda x: x[0] if isinstance(x, list) else x)

    if "coin" not in df.columns:
        logger.debug(f"[{datetime.utcnow()}] Ошибка: в данных нет столбца 'coin'.")
        return

    for coin_id, coin_df in df.groupby("coin"):
        base_collection = f"backup_{mode}_{coin_id}"

        if check_collection_existance(base_collection):
            existing_df = read_from_db(base_collection)
            combined_df = pd.concat([existing_df, coin_df], ignore_index=True)
        else:
            combined_df = coin_df

        combined_df.drop_duplicates(inplace=True)
        write_to_mongo(base_collection, combined_df)
        logger.debug(f"[{datetime.utcnow()}] Данные для {coin_id} сохранены в коллекцию {base_collection} (всего {len(combined_df)} записей).")

def collect_historical_data(coin_id: str):
    """
    Сбор исторических данных для одной монеты и резервное копирование
    """
    headers = {
        "x-cg-pro-api-key": "CG-qmG711yyLriQUS8GE4RfSbed"
    }

    ohlc_url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/ohlc"
    params = {
        "vs_currency": "usd",
        "days": int(CONFIG.get('historical_days', 90))
    }
    ohlc_response = requests.get(ohlc_url, params=params, headers=headers)
    ohlc_response.raise_for_status()
    ohlc_data = ohlc_response.json()

    logger.debug(f"[{datetime.utcnow()}] Получены OHLC данные для {coin_id}")

    logger.debug(f"[{datetime.utcnow()}] Пауза 60 секунд перед запросом volumes для {coin_id}")
    time.sleep(60)

    volume_url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart"
    volume_params = {
        "vs_currency": "usd",
        "days": int(CONFIG.get('historical_days', 90))
    }
    logger.debug(volume_url)
    logger.debug(volume_params)
    volume_response = requests.get(volume_url, params=volume_params, headers=headers)
    volume_response.raise_for_status()
    volume_data = volume_response.json()
    time.sleep(60)

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
    save_backup(records, "historical")

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
            logger.debug(f"[{datetime.utcnow()}] Ошибка при сборе исторических данных для {coin_id}: {e}")

        logger.debug(f"[{datetime.utcnow()}] Пауза 60 секунд перед следующей монетой...")
        time.sleep(60)

    return all_records

def collect_social_data(coin_id: str):
    """
    Сбор постов с Reddit по монете и резервное копирование
    """
    subreddit_name = COINS[coin_id]
    subreddit = reddit.subreddit(subreddit_name)

    time_threshold = datetime.utcnow() - timedelta(hours=CONFIG['collection_interval_hours'])
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
    save_backup(posts, "posts")

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
            logger.debug(f"[{datetime.utcnow()}] Ошибка при сборе постов для {coin_id}: {e}")

    return all_posts