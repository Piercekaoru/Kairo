from fastapi import Depends, FastAPI, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session
import uvicorn

from kairo.api.schemas import FlowListItem, HealthResponse, PaginatedFlows
from kairo.db.base import Base
from kairo.db.session import engine, get_db
from kairo.models.flow import HttpFlow

app = FastAPI(title="Kairo API", version="0.1.0")


@app.on_event("startup")
def on_startup() -> None:
    Base.metadata.create_all(bind=engine)


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(status="ok")


@app.get("/api/v1/flows", response_model=PaginatedFlows)
def list_flows(
    host: str | None = Query(default=None),
    method: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    size: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
) -> PaginatedFlows:
    filters = []
    if host:
        filters.append(HttpFlow.host == host)
    if method:
        filters.append(HttpFlow.method == method.upper())

    total = db.scalar(select(func.count()).select_from(HttpFlow).where(*filters)) or 0
    rows = db.scalars(
        select(HttpFlow)
        .where(*filters)
        .order_by(HttpFlow.created_at.desc())
        .offset((page - 1) * size)
        .limit(size)
    ).all()

    items = [
        FlowListItem(
            id=row.id,
            method=row.method,
            host=row.host,
            path=row.path,
            status_code=row.status_code,
            created_at=row.created_at,
        )
        for row in rows
    ]
    return PaginatedFlows(items=items, total=total)


def run() -> None:
    uvicorn.run("kairo.api.main:app", host="127.0.0.1", port=8000, reload=True)
