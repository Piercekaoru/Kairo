from __future__ import annotations

from datetime import datetime
from enum import Enum
import uuid

from sqlalchemy import DateTime, Enum as SqlEnum, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.sqlite import JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from kairo.db.base import Base


class InterceptState(str, Enum):
    pending = "pending"
    forwarded = "forwarded"
    dropped = "dropped"
    modified = "modified"


class Project(Base):
    __tablename__ = "projects"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    flows: Mapped[list[HttpFlow]] = relationship(back_populates="project", cascade="all, delete-orphan")


class HttpFlow(Base):
    __tablename__ = "http_flows"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id: Mapped[str] = mapped_column(ForeignKey("projects.id"), nullable=False, index=True)
    scheme: Mapped[str] = mapped_column(String(8), nullable=False)
    host: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    port: Mapped[int] = mapped_column(Integer, nullable=False)
    method: Mapped[str] = mapped_column(String(16), nullable=False, index=True)
    path: Mapped[str] = mapped_column(Text, nullable=False)
    query: Mapped[str | None] = mapped_column(Text)
    request_headers: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    request_body: Mapped[str | None] = mapped_column(Text)
    status_code: Mapped[int | None] = mapped_column(Integer, index=True)
    response_headers: Mapped[dict | None] = mapped_column(JSON)
    response_body: Mapped[str | None] = mapped_column(Text)
    duration_ms: Mapped[int | None] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)

    project: Mapped[Project] = relationship(back_populates="flows")
    intercepts: Mapped[list[Intercept]] = relationship(back_populates="flow", cascade="all, delete-orphan")


class Intercept(Base):
    __tablename__ = "intercepts"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    flow_id: Mapped[str] = mapped_column(ForeignKey("http_flows.id"), nullable=False, index=True)
    state: Mapped[InterceptState] = mapped_column(SqlEnum(InterceptState), nullable=False, default=InterceptState.pending)
    modified_request_headers: Mapped[dict | None] = mapped_column(JSON)
    modified_request_body: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    flow: Mapped[HttpFlow] = relationship(back_populates="intercepts")
