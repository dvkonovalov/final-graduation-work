from pydantic import BaseModel
from src.models.historical_record import HistoricalRecord

class HistoricalData(BaseModel):
    data: list[HistoricalRecord]
    path: str | None = None  # Путь к файлу для догрузки данных