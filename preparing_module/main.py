from fastapi import FastAPI
from pydantic import BaseModel
from transformers import pipeline
from bertopic import BERTopic
from sentence_transformers import SentenceTransformer
import pandas as pd
import uvicorn
import os
import umap

# Инициализация FastAPI
app = FastAPI()

# Инициализация моделей
sentiment_pipeline = pipeline("sentiment-analysis", model="nlptown/bert-base-multilingual-uncased-sentiment")
# Загружаем локальную модель
embedding_model = SentenceTransformer('./local_models/all-MiniLM-L6-v2')

umap_model = umap.UMAP(n_neighbors=2, n_components=2, min_dist=0.0, metric='cosine')

# Создаём BERTopic с этой моделью
topic_model = BERTopic(embedding_model=embedding_model, umap_model=umap_model)

# Создаем папку для сохранения файлов
os.makedirs("output", exist_ok=True)

# Описание структуры входных данных
class Post(BaseModel):
    text: str
    timestamp: str  # ISO формат
    hashtags: list[str] = []  # Список строк (может быть пустым)

class PostList(BaseModel):
    posts: list[Post]

# Сентимент маппинг
def map_sentiment(label):
    if "1" in label or "2" in label:
        return -1  # негатив
    elif "3" in label:
        return 0   # нейтрально
    else:
        return 1   # позитив
@app.post("/process-data")
def process_data(post_list: PostList):
    # Преобразование данных в DataFrame
    data = [{
        "text": post.text,
        "timestamp": post.timestamp,
        "hashtags": post.hashtags
    } for post in post_list.posts]

    df = pd.DataFrame(data)
    df['timestamp'] = pd.to_datetime(df['timestamp'])

    # Округляем время по 10 минутам
    df['time_bucket'] = df['timestamp'].dt.floor('10T')

    # Выполним сентимент-анализ
    sentiments = sentiment_pipeline(df['text'].tolist())
    df['sentiment_label'] = [s['label'] for s in sentiments]
    df['sentiment_score'] = [s['score'] for s in sentiments]

    def map_sentiment(label):
        if "1" in label or "2" in label:
            return -1  # негатив
        elif "3" in label:
            return 0   # нейтрально
        else:
            return 1   # позитив

    df['sentiment_mapped'] = df['sentiment_label'].apply(map_sentiment)

    # Выполним тематический анализ
    texts = df['text'].tolist()
    topics, probs = topic_model.fit_transform(texts)
    df['topic'] = topics

    # ---------------- Новый блок создания фичей ----------------

    # Временные признаки
    df['hour_of_day'] = df['timestamp'].dt.hour
    df['day_of_week'] = df['timestamp'].dt.dayofweek  # Monday=0, Sunday=6

    # Объем сообщений в каждом интервале
    volume_by_bucket = df.groupby('time_bucket').size().rename('volume')

    # Агрегация сентимента по времени
    sentiment_agg = df.groupby('time_bucket')['sentiment_mapped'].agg(['mean', 'sum', 'count'])
    sentiment_agg.columns = ['sentiment_mean', 'sentiment_sum', 'sentiment_count']

    # Частота топ-5 тем
    topic_counts = df.groupby(['time_bucket', 'topic']).size().unstack(fill_value=0)
    top_topics = topic_counts.sum(axis=0).sort_values(ascending=False).head(5).index
    topic_counts = topic_counts[top_topics]
    topic_counts.columns = [f"topic_{t}" for t in top_topics]

    # Частота топ-5 хэштегов
    all_hashtags = sum(df['hashtags'], [])
    top_hashtags = pd.Series(all_hashtags).value_counts().head(5).index

    for tag in top_hashtags:
        df[f'hashtag_{tag}'] = df['hashtags'].apply(lambda tags: int(tag in tags))

    hashtag_features = df.groupby('time_bucket')[[f'hashtag_{tag}' for tag in top_hashtags]].sum()

    # Финальный датафрейм признаков
    features = pd.concat([volume_by_bucket, sentiment_agg, topic_counts, hashtag_features], axis=1).fillna(0)

    # ---------------- Конец нового блока ----------------

    # Сохраним результаты
    df.to_csv("output/processed_posts.csv", index=False)        # полный датафрейм постов
    features.to_csv("output/processed_features.csv")             # датафрейм для обучения моделей

    return {
        "status": "success",
        "message": "Data processed and saved to output/processed_posts.csv and output/processed_features.csv",
        "volume_by_time_bucket": volume_by_bucket.to_dict()
    }



# Точка входа для запуска сервера
if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
