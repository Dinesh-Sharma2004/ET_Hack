from app.schemas.briefing import BriefingChatRequest, BriefingChatResponse, BriefingResponse, BriefingSection
from app.schemas.common import Article


class BriefingEngine:
    def generate(self, articles: list[Article]) -> BriefingResponse:
        combined = " ".join(article.summary for article in articles[:4])
        return BriefingResponse(
            headline="Markets, AI Capex, and India Inc. converge into one operating story",
            summary=combined,
            insights=[
                BriefingSection(
                    title="Macro signal",
                    bullets=[
                        "Capital expenditure remains resilient, but leadership is narrowing around AI-linked sectors.",
                        "Rate sensitivity is still shaping financing decisions for startups and mid-cap firms.",
                    ],
                ),
                BriefingSection(
                    title="Execution lens",
                    bullets=[
                        "Founders should watch distribution costs and infra margins before chasing growth narratives.",
                        "Investors should treat earnings commentary as a forward-demand indicator, not just a scorecard.",
                    ],
                ),
            ],
            risks=[
                "AI infrastructure spending could compress near-term margins.",
                "Policy or tariff shifts may disrupt export-linked optimism.",
            ],
            opportunities=[
                "Enterprise AI tooling and semiconductor supply-chain plays remain high-conviction themes.",
                "India-focused digital public infrastructure tailwinds are supporting BFSI and SaaS expansion.",
            ],
            faqs=[
                "Which companies are most exposed to AI capex upside?",
                "How should a retail investor interpret mixed guidance in earnings calls?",
                "What sectors are getting stronger policy support in India?",
            ],
            memory_hint="Conversation memory is seeded with today's macro, AI capex, and India growth signals.",
        )

    def answer(self, payload: BriefingChatRequest, articles: list[Article]) -> BriefingChatResponse:
        mode_prefix = "Explain simply" if payload.mode.lower() == "eli5" else "Expert synthesis"
        matched = [
            article.title
            for article in articles
            if payload.question.lower() in article.content.lower()
            or any(token in article.content.lower() for token in payload.question.lower().split())
        ][:3]
        if not matched:
            matched = [article.title for article in articles[:3]]
        answer = (
            f"{mode_prefix}: {payload.question.strip()} ties back to demand durability, capital discipline, "
            "and second-order effects on valuations. The current article cluster suggests leaders with pricing "
            "power and distribution moats are better positioned than pure narrative plays."
        )
        return BriefingChatResponse(
            answer=answer,
            supporting_articles=matched,
            follow_ups=[
                "Show me the highest-risk scenario over the next quarter.",
                "Translate this into portfolio actions for a balanced investor.",
                "Compare the India angle versus global peers.",
            ],
        )
