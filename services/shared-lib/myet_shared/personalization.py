from collections import defaultdict

from sentence_transformers import SentenceTransformer

from myet_shared.config import EMBEDDING_MODEL
from myet_shared.models import Article, BehaviorSession, NewsCard, UserProfile
from myet_shared.nlp import recency_score


class PersonalizationEngine:
    def __init__(self) -> None:
        self.model = SentenceTransformer(EMBEDDING_MODEL)

    def rank_articles(
        self,
        profile: UserProfile,
        articles: list[Article],
        behavior_sessions: list[BehaviorSession] | None = None,
    ) -> list[NewsCard]:
        if not articles:
            return []

        profile_text = " ".join(
            [profile.role, *profile.interests, *profile.sectors, *profile.portfolio_symbols, profile.risk_appetite]
        )
        article_texts = [" ".join([article.title, article.summary, article.content, article.category, *article.entities]) for article in articles]
        profile_embedding = self.model.encode([profile_text], normalize_embeddings=True)[0]
        article_embeddings = self.model.encode(article_texts, normalize_embeddings=True)
        behavior_weights = self._behavior_weights(behavior_sessions or [])

        cards: list[NewsCard] = []
        for article, embedding in zip(articles, article_embeddings):
            semantic = float(profile_embedding @ embedding)
            interest_overlap = self._interest_overlap(profile, article)
            portfolio_overlap = self._portfolio_overlap(profile, article)
            behavior_score = behavior_weights[article.id]
            freshness = recency_score(article.published_at)
            score = round(
                (semantic * 0.4) + (interest_overlap * 0.2) + (portfolio_overlap * 0.15) + (behavior_score * 0.15) + (freshness * 0.1),
                4,
            )
            reason = self._reason(profile, article, behavior_score, freshness)
            cards.append(
                NewsCard(
                    article_id=article.id,
                    title=article.title,
                    summary=article.summary,
                    category=article.category,
                    relevance_score=score,
                    why_it_matters=reason,
                    entities=article.entities,
                )
            )

        return sorted(cards, key=lambda item: item.relevance_score, reverse=True)

    def _behavior_weights(self, sessions: list[BehaviorSession]) -> defaultdict[str, float]:
        weights: defaultdict[str, float] = defaultdict(float)
        for session in sessions:
            dwell_boost = min(session.dwell_seconds / 600, 1.5)
            for article_id in session.clicked_articles:
                weights[article_id] += 0.35 + (dwell_boost * 0.1)
            for article_id in session.saved_articles:
                weights[article_id] += 0.5
        return weights

    @staticmethod
    def _portfolio_overlap(profile: UserProfile, article: Article) -> float:
        profile_symbols = {symbol.upper() for symbol in profile.portfolio_symbols}
        article_symbols = {entity.upper() for entity in article.entities}
        overlap = len(profile_symbols & article_symbols)
        return overlap / max(len(profile_symbols), 1)

    @staticmethod
    def _interest_overlap(profile: UserProfile, article: Article) -> float:
        haystack = f"{article.title} {article.summary} {article.content} {article.category}".lower()
        terms = [*profile.interests, *profile.sectors]
        matches = sum(1 for term in terms if term.lower() in haystack)
        return matches / max(len(terms), 1)

    @staticmethod
    def _reason(profile: UserProfile, article: Article, behavior_score: float, freshness: float) -> str:
        if any(symbol.upper() in {entity.upper() for entity in article.entities} for symbol in profile.portfolio_symbols):
            return f"Tracked because it overlaps your holdings and recent market activity around {', '.join(article.entities[:2])}."
        if behavior_score > 0.4:
            return f"Elevated because similar readers spent time on related stories and saved adjacent coverage in {article.category}."
        if freshness > 0.6:
            return f"Fresh signal for your {profile.role.lower()} profile with strong relevance to {article.category.lower()}."
        return f"Matched to your interests in {', '.join(article.entities[:2]) or article.category}."
