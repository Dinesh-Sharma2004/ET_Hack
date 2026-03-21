import json
from pathlib import Path

import pandas as pd

from app.core.config import settings
from app.schemas.common import Article
from app.schemas.personalization import OnboardingRequest, UserProfile


class DataRepository:
    def __init__(self) -> None:
        self.root = Path(__file__).resolve().parents[4]
        self.articles_path = (self.root / settings.data_path).resolve()
        self.profile_path = (self.root / settings.profile_store_path).resolve()
        self.portfolio_path = (self.root / settings.portfolio_path).resolve()

    def load_articles(self) -> list[Article]:
        payload = json.loads(self.articles_path.read_text(encoding="utf-8"))
        return [Article(**item) for item in payload["articles"]]

    def get_article(self, article_id: str) -> Article | None:
        return next((article for article in self.load_articles() if article.id == article_id), None)

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
            haystack = " ".join([article.title, article.summary, article.content, article.category, *article.entities]).lower()
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
        if not self.profile_path.exists():
            default = OnboardingRequest(
                role="Investor",
                interests=["Markets", "Macro", "AI"],
                sectors=["Fintech", "Semiconductors"],
                languages=["English", "Hindi"],
                risk_appetite="Balanced",
                portfolio_symbols=["NVDA", "INFY", "TCS"],
            )
            self.save_profile(default)
        payload = json.loads(self.profile_path.read_text(encoding="utf-8"))
        return UserProfile(**payload)

    def save_profile(self, profile: OnboardingRequest) -> UserProfile:
        self.profile_path.write_text(profile.model_dump_json(indent=2), encoding="utf-8")
        return UserProfile(**profile.model_dump(exclude={"onboarding_completed"}))

    def load_portfolio_symbols(self) -> list[str]:
        if not self.portfolio_path.exists():
            return []
        frame = pd.read_csv(self.portfolio_path)
        if "symbol" not in frame.columns:
            return []
        return frame["symbol"].dropna().astype(str).str.upper().tolist()
