from flask import request
from transformers import pipeline
from bertopic import BERTopic
from sentence_transformers import SentenceTransformer
import pandas as pd
import numpy as np
import umap

from src.db import db
from src.logger import logger


sentiment_pipeline = pipeline("sentiment-analysis", model="nlptown/bert-base-multilingual-uncased-sentiment")
embedding_model = SentenceTransformer('./local_models/all-MiniLM-L6-v2')
umap_model = umap.UMAP(n_neighbors=2, n_components=2, min_dist=0.0, metric='cosine')
topic_model = BERTopic(embedding_model=embedding_model, umap_model=umap_model)

def split_and_analyze(texts):
    results = []
    for text in texts:
        chunks = [text[i:i+512] for i in range(0, len(text), 512)]
        chunk_results = []
        for chunk in chunks:
            output = sentiment_pipeline(chunk)
            chunk_results.append(output[0])
        labeles = [float(chunk['score']) * int(chunk['label'][0]) for chunk in chunk_results]
        scores = [float(chunk['score']) for chunk in chunk_results]
        avg_labeles = round(np.mean(labeles))
        results.append({'label': f"{avg_labeles} stars", 'score': np.mean(scores).item()})
    return results


def map_sentiment(label):
    if "1" in label or "2" in label:
        return -1
    elif "3" in label:
        return 0
    else:
        return 1

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

def process_data():
    values = request.get_json()
    post_list = values.get('payload')
    
    if not post_list:
        return {"status": "error", "message": "Not enough data. At least 10 records are required."}
    
    data = [{
        "text": post.get('text'),
        "timestamp": post.get('timestamp'),
        "hashtags": post.get('hashtags')
    } for post in post_list.get('posts')]

    if post_list.get('path'):
        try:
            extra_df = read_from_db(post_list.get('path'))
            extra_df['timestamp'] = pd.to_datetime(extra_df['timestamp'])
            data.extend(extra_df.to_dict(orient='records'))
        except Exception as e:
            return {"status": "error", "message": f"Failed to load collection: {str(e)}"}
    
    if len(data) < 10:
        return {"status": "error", "message": "Not enough data. At least 10 records are required."}

    df = pd.DataFrame(data)
    df['timestamp'] = pd.to_datetime(df['timestamp'])

    if df['text'].isnull().all():
        return {"status": "error", "message": "No valid text data provided for processing"}

    df['time_bucket'] = df['timestamp'].dt.floor('10T')

    sentiments = split_and_analyze(df['text'].tolist())
    df['sentiment_label'] = [s['label'] for s in sentiments]
    df['sentiment_score'] = [s['score'] for s in sentiments]

    df['sentiment_mapped'] = df['sentiment_label'].apply(map_sentiment)

    texts = df['text'].tolist()
    if not texts:
        return {"status": "error", "message": "No valid text data for topic modeling"}

    topics, probs = topic_model.fit_transform(texts)
    df['topic'] = topics


    df['hour_of_day'] = df['timestamp'].dt.hour
    df['day_of_week'] = df['timestamp'].dt.dayofweek

    volume_by_bucket = df.groupby('time_bucket').size().rename('volume')

    sentiment_agg = df.groupby('time_bucket')['sentiment_mapped'].agg(['mean', 'sum', 'count'])
    sentiment_agg.columns = ['sentiment_mean', 'sentiment_sum', 'sentiment_count']

    topic_counts = df.groupby(['time_bucket', 'topic']).size().unstack(fill_value=0)
    top_topics = topic_counts.sum(axis=0).sort_values(ascending=False).head(5).index
    topic_counts = topic_counts[top_topics]
    topic_counts.columns = [f"topic_{t}" for t in top_topics]

    all_hashtags = sum(df['hashtags'], [])
    top_hashtags = pd.Series(all_hashtags).value_counts().head(5).index

    for tag in top_hashtags:
        df[f'hashtag_{tag}'] = df['hashtags'].apply(lambda tags: int(tag in tags))

    hashtag_features = df.groupby('time_bucket')[[f'hashtag_{tag}' for tag in top_hashtags]].sum()

    features = pd.concat([volume_by_bucket, sentiment_agg, topic_counts, hashtag_features], axis=1).fillna(0)

    features["time_bucket"] = features.index
    features.reset_index(drop=True, inplace=True)

    write_to_mongo('processed_posts', df)
    write_to_mongo('processed_features', features)
    
    volume_by_bucket.index = volume_by_bucket.index.astype(str)
    
    return {
        "status": "success",
        "message": "Data processed and saved to processed_posts and processed_features",
        "volume_by_time_bucket": volume_by_bucket.to_dict()
    }

def upload_historical_data():
    values = request.get_json()
    payload = values.get('payload')
    historical_data = payload.get('data')
    if not historical_data:
        return {"status": "error", "message": "Not enough data. At least 1 record is required."}
    data = [{
        "timestamp": record.get('timestamp'),
        "open": record.get('open'),
        "high": record.get('high'),
        "low": record.get('low'),
        "close": record.get('close'),
        "volume": record.get('volume')
    } for record in historical_data]

    df = pd.DataFrame(data)
    df['timestamp'] = pd.to_datetime(df['timestamp'])

    if payload.get('path'):
        try:
            extra_df = read_from_db(historical_data.get('path'))
            extra_df['timestamp'] = pd.to_datetime(extra_df['timestamp'])
            df = pd.concat([extra_df, df], ignore_index=True)
        except Exception as e:
            return {"status": "error", "message": f"Failed to load file: {str(e)}"}

    df = df.sort_values('timestamp')

    write_to_mongo('processed_historical_data', df)

    return {
        "status": "success",
        "message": "Historical data processed and saved to processed_historical_data"
    }