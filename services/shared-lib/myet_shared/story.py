from collections import defaultdict

import networkx as nx

from myet_shared.generation import generate_text
from myet_shared.models import Article
from myet_shared.nlp import compute_sentiment, extract_entities


class StoryArcEngine:
    def build(self, articles: list[Article], story_id: str) -> dict[str, object]:
        related = self._related_articles(articles, story_id)
        graph = nx.Graph()
        sentiment_points = []

        for article in related:
            entities = article.entities or extract_entities(f"{article.title} {article.content}")
            for entity in entities:
                graph.add_node(entity, label=entity, group="company" if entity.isupper() else "theme")
            for source in entities:
                for target in entities:
                    if source == target:
                        continue
                    if graph.has_edge(source, target):
                        graph[source][target]["weight"] += 1
                    else:
                        graph.add_edge(source, target, relation="co-mentioned", weight=1)
            sentiment_points.append(
                {
                    "date": article.published_at,
                    "headline": article.title,
                    "sentiment": round(compute_sentiment(article.content or article.summary), 4),
                    "impact_score": round((len(entities) * 10) + (abs(article.sentiment) * 40), 1),
                }
            )

        nodes = [{"id": node, **data} for node, data in graph.nodes(data=True)]
        relationships = [
            {"source": source, "target": target, "relation": data["relation"], "weight": data["weight"]}
            for source, target, data in graph.edges(data=True)
        ]
        what_next = self._predict_next(sentiment_points, related)
        return {
            "story_id": story_id,
            "arc": {
                "theme": story_id.replace("-", " ").title(),
                "timeline": sorted(sentiment_points, key=lambda item: item["date"], reverse=True),
                "entities": nodes,
                "relationships": sorted(relationships, key=lambda item: item["weight"], reverse=True)[:16],
                "what_next": what_next,
            },
            "related_articles": [article.model_dump() for article in related[:4]],
        }

    def _related_articles(self, articles: list[Article], story_id: str) -> list[Article]:
        key = story_id.lower().replace("-", " ")
        ranked: list[tuple[int, Article]] = []
        for article in articles:
            haystack = " ".join([article.title, article.summary, article.content, article.category, *article.entities]).lower()
            score = haystack.count(key)
            if score:
                ranked.append((score, article))
        if ranked:
            return [article for _, article in sorted(ranked, key=lambda item: item[0], reverse=True)]
        entity_matches = [article for article in articles if any(key in entity.lower() for entity in article.entities)]
        return entity_matches or articles[:6]

    def _predict_next(self, timeline: list[dict], related: list[Article]) -> list[str]:
        if not related:
            return []
        avg_sentiment = sum(item["sentiment"] for item in timeline) / max(len(timeline), 1)
        dominant_categories = defaultdict(int)
        for article in related:
            dominant_categories[article.category] += 1
        category = max(dominant_categories, key=dominant_categories.get)
        direction = "improve" if avg_sentiment >= 0 else "stay pressured"
        most_connected = sorted({entity for article in related for entity in article.entities})[:3]
        generated = generate_text(
            f"Given these business story signals, predict two concise 'what to watch next' bullets.\n"
            f"Category: {category}\nDirection: {direction}\nEntities: {', '.join(most_connected)}\n"
            f"Recent headlines: {' | '.join(article.title for article in related[:5])}",
            max_new_tokens=80,
        )
        bullets = [line.strip("- ").strip() for line in generated.split("\n") if line.strip()]
        return bullets[:2] or [
            f"Coverage in {category.lower()} is likely to stay active as investors watch whether sentiment can {direction}.",
            f"Expect follow-up headlines around {', '.join(most_connected)} as the relationship graph densifies.",
        ]
