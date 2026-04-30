from datetime import date

from pydantic import BaseModel, ConfigDict, Field


class DB13HistoryItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    date: date
    job_name: str
    status: str
    database_size_gb: float = Field(ge=0)
    backup_size_gb: float = Field(ge=0)
    duration_minutes: int = Field(ge=0)
    message: str | None = None


class DB13HistoryResponse(BaseModel):
    system_id: str
    period: str
    items: list[DB13HistoryItem]


class DBGrowthResponse(BaseModel):
    system_id: str
    period: str
    initial_size_gb: float = Field(ge=0)
    current_size_gb: float = Field(ge=0)
    growth_gb: float
    growth_percentage: float


class HealthResponse(BaseModel):
    status: str
    app: str
    environment: str

