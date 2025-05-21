from pydantic import BaseModel

class HistoricalRecord(BaseModel):
    timestamp: str
    open: float
    high: float
    low: float
    close: float
    volume: float
    