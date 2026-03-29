from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, Integer, JSON, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from myet_shared.db import Base


class ArticleRecord(Base):
    __tablename__ = "articles"

    id: Mapped[str] = mapped_column(String(128), primary_key=True)
    title: Mapped[str] = mapped_column(String(1024), nullable=False)
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    category: Mapped[str] = mapped_column(String(128), nullable=False)
    entities: Mapped[list[str]] = mapped_column(JSON, default=list)
    sentiment: Mapped[float] = mapped_column(Float, default=0.0)
    language: Mapped[str] = mapped_column(String(64), default="English")
    published_at: Mapped[datetime] = mapped_column(DateTime, index=True)
    source: Mapped[str] = mapped_column(String(256), default="Unknown")
    read_time_minutes: Mapped[int] = mapped_column(Integer, default=1)
    url: Mapped[str | None] = mapped_column(String(2048), nullable=True, unique=True)
    image_url: Mapped[str | None] = mapped_column(String(2048), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class UserProfileRecord(Base):
    __tablename__ = "user_profiles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, default=1)
    role: Mapped[str] = mapped_column(String(128), default="Investor")
    interests: Mapped[list[str]] = mapped_column(JSON, default=list)
    sectors: Mapped[list[str]] = mapped_column(JSON, default=list)
    languages: Mapped[list[str]] = mapped_column(JSON, default=list)
    risk_appetite: Mapped[str] = mapped_column(String(64), default="Balanced")
    portfolio_symbols: Mapped[list[str]] = mapped_column(JSON, default=list)
    onboarding_completed: Mapped[bool] = mapped_column(Boolean, default=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class BehaviorSessionRecord(Base):
    __tablename__ = "behavior_sessions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_segment: Mapped[str] = mapped_column(String(128), index=True)
    clicked_articles: Mapped[list[str]] = mapped_column(JSON, default=list)
    saved_articles: Mapped[list[str]] = mapped_column(JSON, default=list)
    dwell_seconds: Mapped[int] = mapped_column(Integer, default=0)
    preferred_mode: Mapped[str] = mapped_column(String(64), default="expert")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class VideoAssetRecord(Base):
    __tablename__ = "video_assets"
    __table_args__ = (UniqueConstraint("article_id", name="uq_video_asset_article"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    article_id: Mapped[str] = mapped_column(String(128), index=True)
    title: Mapped[str] = mapped_column(String(1024))
    status: Mapped[str] = mapped_column(String(64), default="ready")
    video_path: Mapped[str] = mapped_column(String(2048))
    audio_path: Mapped[str | None] = mapped_column(String(2048), nullable=True)
    runtime_seconds: Mapped[int] = mapped_column(Integer, default=0)
    script: Mapped[list[str]] = mapped_column(JSON, default=list)
    highlights: Mapped[list[str]] = mapped_column(JSON, default=list)
    segments: Mapped[list[dict]] = mapped_column(JSON, default=list)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
