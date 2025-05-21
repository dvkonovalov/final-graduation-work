from pydantic import BaseModel
from src.models.post import Post

class PostList(BaseModel):
    posts: list[Post]
    path: str | None = None  # Путь к файлу для догрузки данных