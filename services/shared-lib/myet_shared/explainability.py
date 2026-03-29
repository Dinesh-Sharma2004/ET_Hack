from myet_shared.models import Article, UserProfile


class RecommendationExplainer:
    def explain(self, profile: UserProfile, article: Article) -> dict[str, object]:
        interest_matches = [
            interest for interest in profile.interests if interest.lower() in article.content.lower() or interest.lower() in article.title.lower()
        ]
        sector_matches = [
            sector for sector in profile.sectors if sector.lower() in article.content.lower() or sector.lower() in article.title.lower()
        ]
        portfolio_matches = [
            symbol for symbol in profile.portfolio_symbols if symbol.upper() in {entity.upper() for entity in article.entities}
        ]
        return {
            "article_id": article.id,
            "interest_matches": interest_matches,
            "sector_matches": sector_matches,
            "portfolio_matches": portfolio_matches,
            "reason_summary": self._summary(interest_matches, sector_matches, portfolio_matches),
        }

    def _summary(self, interest_matches: list[str], sector_matches: list[str], portfolio_matches: list[str]) -> str:
        if portfolio_matches:
            return f"Shown because it overlaps with holdings: {', '.join(portfolio_matches)}."
        if sector_matches:
            return f"Shown because it matches sectors: {', '.join(sector_matches)}."
        if interest_matches:
            return f"Shown because it aligns with interests: {', '.join(interest_matches)}."
        return "Shown because the semantic ranker found strong behavioral relevance."
