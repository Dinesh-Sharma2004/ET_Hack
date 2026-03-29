from collections import defaultdict

from myet_shared.generation import generate_text
from myet_shared.models import Article, RetrievalHit
from myet_shared.nlp import extract_risks_and_opportunities, top_sentences


class BriefingComposer:
    def compose(self, topic: str, hits: list[RetrievalHit], article_lookup: dict[str, Article]) -> dict[str, object]:
        related_articles = [article_lookup[hit.article_id].model_dump() for hit in hits if hit.article_id in article_lookup]
        combined_text = " ".join(hit.text for hit in hits)
        summary_sentences = top_sentences(topic, combined_text, limit=3)
        generated_summary = generate_text(
            f"Summarize this business briefing for topic '{topic}' in 3 concise sentences:\n{combined_text[:2400]}",
            max_new_tokens=140,
        )
        insights = self._insights(topic, hits, article_lookup)
        risks, opportunities = extract_risks_and_opportunities(summary_sentences + [hit.text for hit in hits])
        return {
            "topic": topic,
            "report": {
                "headline": f"{topic.title()} briefing",
                "summary": generated_summary or " ".join(summary_sentences),
                "insights": insights,
                "risks": risks or [sentence for sentence in summary_sentences[-2:]],
                "opportunities": opportunities or [sentence for sentence in summary_sentences[:2]],
            },
            "related_articles": related_articles[:4],
            "suggested_questions": self._suggested_questions(topic, hits, article_lookup),
            "sources": [hit.model_dump() for hit in hits],
        }

    def answer(self, topic: str, question: str, hits: list[RetrievalHit], article_lookup: dict[str, Article]) -> dict[str, object]:
        supporting_articles = [article_lookup[hit.article_id].title for hit in hits if hit.article_id in article_lookup]
        answer_sentences = top_sentences(question or topic, " ".join(hit.text for hit in hits), limit=3)
        generated_answer = generate_text(
            f"Answer the question using the supplied business news context.\nQuestion: {question or topic}\nContext: {' '.join(hit.text for hit in hits)[:2400]}",
            max_new_tokens=120,
        )
        return {
            "topic": topic,
            "response": {
                "answer": generated_answer or " ".join(answer_sentences),
                "supporting_articles": supporting_articles[:4],
            },
            "sources": [hit.model_dump() for hit in hits],
        }

    def _insights(self, topic: str, hits: list[RetrievalHit], article_lookup: dict[str, Article]) -> list[dict[str, object]]:
        category_buckets: defaultdict[str, list[str]] = defaultdict(list)
        for hit in hits:
            article = article_lookup.get(hit.article_id)
            if not article:
                continue
            category_buckets[article.category].extend(top_sentences(topic, hit.text, limit=2))
        sections = []
        for category, bullets in list(category_buckets.items())[:3]:
            synthesized = generate_text(
                f"Write 2 short business insights about {category} within the topic {topic} using this context: {' '.join(bullets)[:1200]}",
                max_new_tokens=90,
            )
            sections.append({"title": category, "bullets": bullets[:3]})
            if synthesized:
                sections[-1]["bullets"] = [line.strip("- ").strip() for line in synthesized.split("\n") if line.strip()][:3] or bullets[:3]
        return sections or [{"title": "Key signal", "bullets": [hit.text for hit in hits[:2]]}]

    def _suggested_questions(self, topic: str, hits: list[RetrievalHit], article_lookup: dict[str, Article]) -> list[str]:
        entities = []
        for hit in hits:
            article = article_lookup.get(hit.article_id)
            if article:
                entities.extend(article.entities)
        unique_entities = [entity for index, entity in enumerate(entities) if entity and entity not in entities[:index]]
        prompts = [
            f"What is the biggest risk in {topic} over the next quarter?",
            f"Which companies are best positioned in {topic} right now?",
        ]
        if unique_entities:
            prompts.append(f"How should I interpret the latest moves by {unique_entities[0]}?")
        return prompts[:3]
