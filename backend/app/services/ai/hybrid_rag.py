from __future__ import annotations

from collections import Counter
from dataclasses import dataclass

from app.schemas.common import Article
from app.services.ai.embeddings import cosine_similarity, embed_text


@dataclass
class RetrievalResult:
    article: Article
    dense_score: float
    keyword_score: float
    combined_score: float


class HybridRetriever:
    """Production-style sample retriever that mixes dense and keyword scores."""

    def retrieve(self, query: str, articles: list[Article], top_k: int = 5) -> list[RetrievalResult]:
        query_embedding = embed_text(query)
        query_terms = Counter(query.lower().split())
        results: list[RetrievalResult] = []

        for article in articles:
            article_text = " ".join([article.title, article.summary, article.content, article.category, *article.entities])
            article_embedding = embed_text(article_text)
            dense_score = cosine_similarity(query_embedding, article_embedding)

            haystack_terms = Counter(article_text.lower().split())
            keyword_hits = sum(query_terms[term] for term in query_terms if haystack_terms[term] > 0)
            keyword_score = keyword_hits / max(sum(query_terms.values()), 1)
            combined_score = round((dense_score * 0.7) + (keyword_score * 0.3), 4)

            results.append(
                RetrievalResult(
                    article=article,
                    dense_score=round(dense_score, 4),
                    keyword_score=round(keyword_score, 4),
                    combined_score=combined_score,
                )
            )

        return sorted(results, key=lambda item: item.combined_score, reverse=True)[:top_k]


class AgenticBriefingOrchestrator:
    """
    Sample orchestration layer that demonstrates:
    1. query decomposition
    2. retrieval
    3. synthesis
    """

    def __init__(self) -> None:
        self.retriever = HybridRetriever()

    def answer(self, query: str, articles: list[Article]) -> dict[str, object]:
        sub_queries = self._decompose_query(query)
        retrievals = {
            sub_query: self.retriever.retrieve(sub_query, articles, top_k=3) for sub_query in sub_queries
        }
        retrieved_articles = []
        seen_ids: set[str] = set()
        for hits in retrievals.values():
            for hit in hits:
                if hit.article.id not in seen_ids:
                    retrieved_articles.append(hit.article)
                    seen_ids.add(hit.article.id)

        answer = self._synthesize(query, retrieved_articles)
        return {
            "query": query,
            "sub_queries": sub_queries,
            "retrieved_article_ids": [article.id for article in retrieved_articles],
            "answer": answer,
        }

    def _decompose_query(self, query: str) -> list[str]:
        words = query.lower().split()
        if "risk" in words:
            return [query, "market risk outlook", "earnings downside signals"]
        if "india" in words:
            return [query, "india policy tailwinds", "domestic sector beneficiaries"]
        return [query, "market context", "company and sector implications"]

    def _synthesize(self, query: str, articles: list[Article]) -> str:
        if not articles:
            return "No relevant evidence was found, so the assistant should fall back to a broader market summary."
        top_titles = ", ".join(article.title for article in articles[:3])
        return (
            f"Agentic synthesis for '{query}': retrieved evidence suggests the strongest signals come from {top_titles}. "
            "A production LLM would merge these sources into a grounded, cited answer."
        )
