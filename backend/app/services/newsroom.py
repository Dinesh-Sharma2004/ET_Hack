from io import BytesIO

import pandas as pd

from app.schemas.common import Article, MetricCard
from app.schemas.page_models import (
    DashboardOverviewResponse,
    FilterOptionsResponse,
    NewsFeedResponse,
    PortfolioUploadResponse,
    ProfileUpdateRequest,
    RecommendationFeedResponse,
)
from app.schemas.personalization import DashboardResponse, OnboardingRequest, RecommendationResponse, UserProfile
from app.services.ai.personalization import PersonalizationEngine
from app.services.ai.translation import VernacularEngine
from app.services.data.loader import DataRepository


class NewsroomService:
    def __init__(self, repository: DataRepository) -> None:
        self.repository = repository
        self.engine = PersonalizationEngine()
        self.vernacular = VernacularEngine()

    def build_dashboard(self) -> DashboardResponse:
        profile = self.repository.load_profile()
        articles = self.repository.load_articles()
        recommendations = self.engine.rank_articles(profile, articles)
        return DashboardResponse(
            profile=profile,
            featured=recommendations[:4],
            deep_briefings=recommendations[4:8],
            metrics=[
                MetricCard(label="Signal Match", value="92%", delta="+8%"),
                MetricCard(label="Portfolio Coverage", value="11 stocks", delta="+3"),
                MetricCard(label="Briefing Depth", value="4 layers", delta="Live"),
            ],
            translations=self.vernacular.translate_feature(articles[0]),
        )

    def save_profile(self, payload: OnboardingRequest) -> UserProfile:
        return self.repository.save_profile(payload)

    def get_dashboard_overview(self) -> DashboardOverviewResponse:
        dashboard = self.build_dashboard()
        trending = sorted(self.repository.load_articles(), key=lambda article: article.sentiment, reverse=True)[:3]
        return DashboardOverviewResponse(
            profile=dashboard.profile,
            feed=dashboard.featured,
            highlights=dashboard.metrics,
            trending=trending,
        )

    def get_news_feed(
        self,
        category: str | None = None,
        stock: str | None = None,
        interest: str | None = None,
        search: str | None = None,
        offset: int = 0,
        limit: int = 10,
    ) -> NewsFeedResponse:
        articles = self.repository.search_articles(category=category, stock=stock, interest=interest, search=search)
        page = articles[offset : offset + limit]
        highlights = [
            MetricCard(label="Stories indexed", value=str(len(articles)), delta="live"),
            MetricCard(label="Industries", value=str(len({article.category for article in articles})), delta="active"),
            MetricCard(label="Tracked entities", value=str(len({entity for article in articles for entity in article.entities})), delta="connected"),
        ]
        trending_topics = sorted({entity for article in articles for entity in article.entities})[:6]
        return NewsFeedResponse(
            items=page,
            total=len(articles),
            offset=offset,
            limit=limit,
            highlights=highlights,
            trending_topics=trending_topics,
        )

    def get_recommendations(
        self,
        industry: str | None = None,
        stock: str | None = None,
        interest: str | None = None,
    ) -> RecommendationFeedResponse:
        profile = self.repository.load_profile()
        articles = self.repository.search_articles(category=industry, stock=stock, interest=interest)
        ranked = self.engine.rank_articles(profile, articles or self.repository.load_articles())
        all_articles = self.repository.load_articles()
        filters = FilterOptionsResponse(
            industries=sorted({article.category for article in all_articles}),
            stocks=sorted({entity for article in all_articles for entity in article.entities if entity.isupper()}),
            interests=sorted({term for article in all_articles for term in [article.category, *article.entities]}),
        )
        return RecommendationFeedResponse(
            profile=profile,
            items=ranked,
            total=len(ranked),
            filters=filters.model_dump(),
        )

    def update_profile(self, payload: ProfileUpdateRequest) -> UserProfile:
        onboarding = OnboardingRequest(**payload.model_dump())
        return self.repository.save_profile(onboarding)

    def recommend_from_portfolio_bytes(self, content: bytes, filename: str) -> RecommendationResponse:
        frame = pd.read_csv(BytesIO(content))
        symbols = frame.iloc[:, 0].dropna().astype(str).str.upper().tolist()
        profile = self.repository.load_profile()
        enriched_payload = profile.model_dump()
        enriched_payload["portfolio_symbols"] = symbols
        enriched = UserProfile(**enriched_payload)
        recommendations = self.engine.rank_articles(enriched, self.repository.load_articles())[:5]
        return RecommendationResponse(profile=enriched, recommendations=recommendations)

    def upload_portfolio(self, content: bytes, filename: str) -> PortfolioUploadResponse:
        response = self.recommend_from_portfolio_bytes(content, filename)
        return PortfolioUploadResponse(profile=response.profile, items=response.recommendations)

    def get_translated_article(self, article_id: str, language: str, mode: str) -> tuple[str, str]:
        article = self.repository.get_article(article_id) or self.repository.load_articles()[0]
        translations = self.vernacular.translate_feature(article)
        contextual = translations.get(language, article.summary)
        if mode == "literal":
            return article.title, f"{article.summary} ({language} literal adaptation)"
        return article.title, contextual
