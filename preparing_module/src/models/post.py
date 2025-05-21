from pydantic import BaseModel

class Post(BaseModel):
    text: str
    timestamp: str  # ISO формат
    hashtags: list[str] = []