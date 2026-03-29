import json
from pathlib import Path
from datetime import UTC

from sqlalchemy import delete, select
from sqlalchemy.exc import IntegrityError

from myet_shared.config import ROOT_DIR
from myet_shared.db import Base, engine, session_scope
from myet_shared.models import Article, BehaviorSession, UserProfile
from myet_shared.nlp import parse_datetime
from myet_shared.orm import ArticleRecord, BehaviorSessionRecord, UserProfileRecord, VideoAssetRecord


class SharedRepository:
    def __init__(self, root: str | None = None) -> None:
        self.root = Path(root) if root else ROOT_DIR
        self.sample_dir = self.root / "shared" / "sample_data"
        try:
            Base.metadata.create_all(engine)
        except IntegrityError:
            pass
        self._bootstrap_if_needed()

    def _bootstrap_if_needed(self) -> None:
        with session_scope() as session:
            profile_exists = session.scalar(select(UserProfileRecord.id).limit(1))
            if not profile_exists:
                session.add(
                    UserProfileRecord(
                        id=1,
                        role="Investor",
                        interests=["Markets", "AI"],
                        sectors=["Technology", "Finance"],
                        languages=["English", "Hindi"],
                        risk_appetite="Balanced",
                        portfolio_symbols=["NVDA", "INFY", "TCS", "HDFCBANK"],
                        onboarding_completed=True,
                    )
                )

            behavior_exists = session.scalar(select(BehaviorSessionRecord.id).limit(1))
            behavior_path = self.sample_dir / "user_behavior.json"
            if not behavior_exists and behavior_path.exists():
                payload = json.loads(behavior_path.read_text(encoding="utf-8"))
                for item in payload.get("sessions", []):
                    session.add(
                        BehaviorSessionRecord(
                            user_segment=item.get("user_segment", "Investor"),
                            clicked_articles=item.get("clicked_articles", []),
                            saved_articles=item.get("saved_articles", []),
                            dwell_seconds=item.get("dwell_seconds", 0),
                            preferred_mode=item.get("preferred_mode", "expert"),
                        )
                    )

    def load_articles(self) -> list[Article]:
        with session_scope() as session:
            records = session.scalars(select(ArticleRecord).order_by(ArticleRecord.published_at.desc())).all()
            return [self._article_from_record(record) for record in records]

    def get_article(self, article_id: str) -> Article | None:
        with session_scope() as session:
            record = session.get(ArticleRecord, article_id)
            return self._article_from_record(record) if record else None

    def upsert_articles(self, articles: list[Article]) -> list[Article]:
        if not articles:
            return []
        with session_scope() as session:
            for article in articles:
                existing = session.get(ArticleRecord, article.id)
                payload = article.model_dump()
                payload["published_at"] = parse_datetime(payload["published_at"]).replace(tzinfo=None)
                if existing:
                    for key, value in payload.items():
                        setattr(existing, key, value)
                else:
                    session.add(ArticleRecord(**payload))
        return articles

    def search_articles(
        self,
        category: str | None = None,
        stock: str | None = None,
        interest: str | None = None,
        search: str | None = None,
    ) -> list[Article]:
        articles = self.load_articles()
        filtered: list[Article] = []
        for article in articles:
            haystack = " ".join(
                [
                    article.title,
                    article.summary,
                    article.content,
                    article.category,
                    *article.entities,
                    article.source,
                ]
            ).lower()
            if category and article.category.lower() != category.lower():
                continue
            if stock and stock.upper() not in {entity.upper() for entity in article.entities}:
                continue
            if interest and interest.lower() not in haystack:
                continue
            if search and search.lower() not in haystack:
                continue
            filtered.append(article)
        return filtered

    def load_profile(self) -> UserProfile:
        with session_scope() as session:
            record = session.get(UserProfileRecord, 1)
            if not record:
                record = UserProfileRecord(id=1)
                session.add(record)
                session.flush()
            return UserProfile(
                role=record.role,
                interests=record.interests or [],
                sectors=record.sectors or [],
                languages=record.languages or [],
                risk_appetite=record.risk_appetite,
                portfolio_symbols=record.portfolio_symbols or [],
                onboarding_completed=record.onboarding_completed,
            )

    def save_profile(self, profile: UserProfile) -> UserProfile:
        with session_scope() as session:
            record = session.get(UserProfileRecord, 1)
            if not record:
                record = UserProfileRecord(id=1)
                session.add(record)
            record.role = profile.role
            record.interests = profile.interests
            record.sectors = profile.sectors
            record.languages = profile.languages
            record.risk_appetite = profile.risk_appetite
            record.portfolio_symbols = profile.portfolio_symbols
            record.onboarding_completed = profile.onboarding_completed
        return profile

    def load_portfolio_symbols(self) -> list[str]:
        return self.load_profile().portfolio_symbols

    def save_portfolio_symbols(self, symbols: list[str]) -> list[str]:
        profile = self.load_profile()
        profile.portfolio_symbols = [symbol.upper() for symbol in symbols]
        self.save_profile(profile)
        return profile.portfolio_symbols

    def load_behavior_sessions(self) -> list[BehaviorSession]:
        with session_scope() as session:
            records = session.scalars(select(BehaviorSessionRecord).order_by(BehaviorSessionRecord.created_at.desc())).all()
            return [
                BehaviorSession(
                    user_segment=record.user_segment,
                    clicked_articles=record.clicked_articles or [],
                    saved_articles=record.saved_articles or [],
                    dwell_seconds=record.dwell_seconds,
                    preferred_mode=record.preferred_mode,
                )
                for record in records
            ]

    def replace_behavior_sessions(self, sessions: list[BehaviorSession]) -> None:
        with session_scope() as session:
            session.execute(delete(BehaviorSessionRecord))
            for item in sessions:
                session.add(
                    BehaviorSessionRecord(
                        user_segment=item.user_segment,
                        clicked_articles=item.clicked_articles,
                        saved_articles=item.saved_articles,
                        dwell_seconds=item.dwell_seconds,
                        preferred_mode=item.preferred_mode,
                    )
                )

    def load_video_asset(self, article_id: str) -> VideoAssetRecord | None:
        with session_scope() as session:
            return session.scalar(select(VideoAssetRecord).where(VideoAssetRecord.article_id == article_id))

    def save_video_asset(
        self,
        article_id: str,
        title: str,
        video_path: str,
        audio_path: str | None,
        runtime_seconds: int,
        script: list[str],
        highlights: list[str],
        segments: list[dict],
    ) -> None:
        with session_scope() as session:
            record = session.scalar(select(VideoAssetRecord).where(VideoAssetRecord.article_id == article_id))
            if not record:
                record = VideoAssetRecord(article_id=article_id, title=title, video_path=video_path)
                session.add(record)
            record.title = title
            record.video_path = video_path
            record.audio_path = audio_path
            record.runtime_seconds = runtime_seconds
            record.script = script
            record.highlights = highlights
            record.segments = segments

    def available_filters(self) -> dict[str, list[str]]:
        articles = self.load_articles()
        return {
            "industries": sorted({article.category for article in articles}),
            "stocks": sorted({entity for article in articles for entity in article.entities if entity.isupper()})[:30],
            "interests": sorted({token for article in articles for token in [article.category, *article.entities]})[:30],
        }

    @staticmethod
    def _article_from_record(record: ArticleRecord) -> Article:
        return Article(
            id=record.id,
            title=record.title,
            summary=record.summary,
            content=record.content,
            category=record.category,
            entities=record.entities or [],
            sentiment=record.sentiment,
            language=record.language,
            published_at=record.published_at.replace(tzinfo=UTC).isoformat(),
            source=record.source,
            read_time_minutes=record.read_time_minutes,
            url=record.url,
            image_url=record.image_url,
        )
