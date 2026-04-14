from datetime import datetime, timezone
from uuid import UUID, uuid4

from sqlalchemy import String, DateTime, JSON, Enum as SQLEnum, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from app.domain.models.value_objects import OutputFormat, ReportStatus


class Base(DeclarativeBase):
    pass


class TemplateModel(Base):
    __tablename__ = "report_templates"

    id: Mapped[UUID] = mapped_column(primary_key=True, index=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(index=True)
    name: Mapped[str] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(String(1000))
    columns: Mapped[list] = mapped_column(JSON)
    output_format: Mapped[OutputFormat] = mapped_column(SQLEnum(OutputFormat))
    styling: Mapped[dict | None] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )


class ReportModel(Base):
    __tablename__ = "reports"

    id: Mapped[UUID] = mapped_column(primary_key=True, index=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(index=True)
    template_id: Mapped[UUID] = mapped_column(ForeignKey("report_templates.id"))
    status: Mapped[ReportStatus] = mapped_column(SQLEnum(ReportStatus))
    database_source: Mapped[dict | None] = mapped_column(JSON)
    inline_data: Mapped[dict | None] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )
    started_at: Mapped[datetime | None] = mapped_column(DateTime)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime)
    file_key: Mapped[str | None] = mapped_column(String(500))
    error_message: Mapped[str | None] = mapped_column(String)
