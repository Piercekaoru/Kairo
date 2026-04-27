from datetime import datetime

from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str


class FlowListItem(BaseModel):
    id: str
    method: str
    host: str
    path: str
    status_code: int | None
    created_at: datetime


class PaginatedFlows(BaseModel):
    items: list[FlowListItem]
    total: int
