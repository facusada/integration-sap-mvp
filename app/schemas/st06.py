from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ST06HistoryItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    timestamp: datetime
    host: str
    category: str
    metric: str
    value: float | str
    unit: str | None = None
    message: str | None = None


class ST06HistoryResponse(BaseModel):
    system_id: str
    period: str
    host: str | None = None
    category: str | None = None
    items: list[ST06HistoryItem]

