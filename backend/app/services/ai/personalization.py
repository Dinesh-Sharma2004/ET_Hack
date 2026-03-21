from statistics import mean

from app.schemas.common import Article, NewsCard
from app.schemas.personalization import UserProfile
from app.services.ai.embeddings import cosine_similarity, embed_text


class PersonalizationEngine:
    def rank_articles(self, profile: UserProfile, articles: list[Article]) -> list[NewsCard]:
        profile_text = " ".join(
            [profile.role, *profile.interests, *profile.sectors, *profile.portfolio_symbols, profile.risk_appetite]
        )
        profile_embedding = embed_text(profile_text)
        cards: list[NewsCard] = []

        for article in articles:
            article_embedding = embed_text(
                " ".join([article.title, article.summary, article.content, article.category, *article.entities])
            )
            similarity = cosine_similarity(profile_embedding, article_embedding)
            entity_overlap = len(set(map(str.upper, profile.portfolio_symbols)) & set(map(str.upper, article.entities)))
            interest_overlap = mean(
                [
                    1.0 if term.lower() in article.content.lower() or term.lower() in article.title.lower() else 0.0
                    for term in [*profile.interests, *profile.sectors]
                ]
                or [0.0]
            )
            score = round((similarity * 0.5) + (interest_overlap * 0.35) + (entity_overlap * 0.15), 3)
            cards.append(
                NewsCard(
                    article_id=article.id,
                    title=article.title,
                    summary=article.summary,
                    category=article.category,
                    relevance_score=score,
                    why_it_matters=self._why_it_matters(profile, article, entity_overlap),
                    entities=article.entities,
                )
            )

        return sorted(cards, key=lambda card: card.relevance_score, reverse=True)

    def _why_it_matters(self, profile: UserProfile, article: Article, entity_overlap: int) -> str:
        if entity_overlap:
            return f"Portfolio overlap detected across {entity_overlap} tracked holdings."
        if article.category in profile.interests:
            return f"Strong match for your {article.category.lower()} interest profile."
        return f"Relevant to your {profile.role.lower()} workflow with signals in {', '.join(article.entities[:2])}."
