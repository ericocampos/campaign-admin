import enum
from datetime import date, datetime, timezone

from sqlalchemy import Date, DateTime, Enum, ForeignKey, Index, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, onupdate=utcnow, nullable=False
    )


class CampaignStatus(str, enum.Enum):
    draft = "draft"
    active = "active"
    paused = "paused"
    done = "done"
    archived = "archived"


class Campaign(Base, TimestampMixin):
    __tablename__ = "campaigns"

    id: Mapped[int] = mapped_column(primary_key=True)
    slug: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    status: Mapped[CampaignStatus] = mapped_column(
        Enum(CampaignStatus, name="campaign_status"),
        default=CampaignStatus.draft,
        nullable=False,
    )
    start_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    end_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    overview: Mapped[str] = mapped_column(Text, default="", nullable=False)

    steps: Mapped[list["Step"]] = relationship(
        back_populates="campaign", cascade="all, delete-orphan", order_by="Step.sequence"
    )
    checklist_items: Mapped[list["ChecklistItem"]] = relationship(
        back_populates="campaign",
        cascade="all, delete-orphan",
        order_by="(ChecklistItem.group_name, ChecklistItem.sequence)",
    )
    log_entries: Mapped[list["LogEntry"]] = relationship(
        back_populates="campaign",
        cascade="all, delete-orphan",
        order_by="LogEntry.occurred_at.desc()",
    )


class StepStatus(str, enum.Enum):
    planned = "planned"
    live = "live"
    done = "done"
    skipped = "skipped"


class Step(Base, TimestampMixin):
    __tablename__ = "steps"

    id: Mapped[int] = mapped_column(primary_key=True)
    campaign_id: Mapped[int] = mapped_column(
        ForeignKey("campaigns.id", ondelete="CASCADE"), nullable=False
    )
    sequence: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    channel: Mapped[str] = mapped_column(String(100), default="", nullable=False)
    status: Mapped[StepStatus] = mapped_column(
        Enum(StepStatus, name="step_status"), default=StepStatus.planned, nullable=False
    )
    scheduled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    posted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    metrics: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    content: Mapped[str] = mapped_column(Text, default="", nullable=False)
    retro: Mapped[str] = mapped_column(Text, default="", nullable=False)

    campaign: Mapped[Campaign] = relationship(back_populates="steps")

    __table_args__ = (Index("ix_steps_campaign_sequence", "campaign_id", "sequence"),)


class ChecklistStatus(str, enum.Enum):
    pending = "pending"
    done = "done"
    blocked = "blocked"


class ChecklistItem(Base, TimestampMixin):
    __tablename__ = "checklist_items"

    id: Mapped[int] = mapped_column(primary_key=True)
    campaign_id: Mapped[int] = mapped_column(
        ForeignKey("campaigns.id", ondelete="CASCADE"), nullable=False
    )
    group_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    sequence: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    text: Mapped[str] = mapped_column(String(500), nullable=False)
    status: Mapped[ChecklistStatus] = mapped_column(
        Enum(ChecklistStatus, name="checklist_status"),
        default=ChecklistStatus.pending,
        nullable=False,
    )
    done_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    notes: Mapped[str] = mapped_column(Text, default="", nullable=False)

    campaign: Mapped[Campaign] = relationship(back_populates="checklist_items")

    __table_args__ = (
        Index("ix_checklist_campaign_group_seq", "campaign_id", "group_name", "sequence"),
    )


class LogEntry(Base, TimestampMixin):
    __tablename__ = "log_entries"

    id: Mapped[int] = mapped_column(primary_key=True)
    campaign_id: Mapped[int] = mapped_column(
        ForeignKey("campaigns.id", ondelete="CASCADE"), nullable=False
    )
    category: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    body: Mapped[str] = mapped_column(Text, default="", nullable=False)
    count: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    status: Mapped[str | None] = mapped_column(String(50), nullable=True)
    source: Mapped[str | None] = mapped_column(String(200), nullable=True)
    occurred_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, nullable=False
    )

    campaign: Mapped[Campaign] = relationship(back_populates="log_entries")

    __table_args__ = (
        Index("ix_logs_campaign_category_time", "campaign_id", "category", "occurred_at"),
    )
