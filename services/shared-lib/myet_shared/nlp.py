import re
from collections import Counter
from datetime import UTC, datetime
from functools import lru_cache

import numpy as np
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer


RISK_TERMS = {
    "risk",
    "slowdown",
    "pressure",
    "compliance",
    "cost",
    "volatility",
    "uncertain",
    "burn",
    "margin",
    "tightens",
    "delay",
}
OPPORTUNITY_TERMS = {
    "growth",
    "tailwind",
    "opportunity",
    "expand",
    "advantage",
    "demand",
    "moat",
    "accelerate",
    "scale",
    "profitability",
}


@lru_cache(maxsize=1)
def _sentiment_model():
    return SentimentIntensityAnalyzer()


def compute_sentiment(text: str) -> float:
    return float(_sentiment_model().polarity_scores(text)["compound"])


def estimate_read_time(text: str) -> int:
    words = max(len(text.split()), 1)
    return max(round(words / 180), 1)


def parse_datetime(value: str | None) -> datetime:
    if not value:
        return datetime.now(UTC)
    normalized = value.replace("Z", "+00:00")
    try:
        parsed = datetime.fromisoformat(normalized)
        if parsed.tzinfo is None:
            return parsed.replace(tzinfo=UTC)
        return parsed.astimezone(UTC)
    except ValueError:
        return datetime.now(UTC)


def extract_entities(text: str) -> list[str]:
    ticker_like = re.findall(r"\b[A-Z]{2,10}\b", text)
    titled_phrases = re.findall(r"\b(?:[A-Z][a-z]+(?:\s+[A-Z][a-z]+){0,2})\b", text)
    entities = []
    for token in [*ticker_like, *titled_phrases]:
        clean = token.strip()
        if clean and clean not in entities and clean.lower() not in {"The", "And", "For"}:
            entities.append(clean)
    return entities[:12]


def classify_category(text: str) -> str:
    lowered = text.lower()
    category_keywords = {
        "AI": ["ai", "artificial intelligence", "chip", "semiconductor", "cloud"],
        "Fintech": ["fintech", "bank", "payments", "upi", "lending"],
        "Markets": ["market", "earnings", "stocks", "investor", "equity"],
        "Startups": ["startup", "founder", "venture", "burn", "gmv"],
        "Energy": ["oil", "energy", "crude", "gas", "refining"],
        "Manufacturing": ["factory", "manufacturing", "battery", "ev", "supply chain"],
        "Enterprise": ["compliance", "enterprise", "sovereign", "vendor", "saas"],
    }
    for category, keywords in category_keywords.items():
        if any(keyword in lowered for keyword in keywords):
            return category
    return "Business"


def chunk_text(text: str, chunk_size: int = 120, overlap: int = 30) -> list[str]:
    words = text.split()
    if len(words) <= chunk_size:
        return [text]
    chunks = []
    start = 0
    while start < len(words):
        end = min(start + chunk_size, len(words))
        chunks.append(" ".join(words[start:end]))
        if end == len(words):
            break
        start = max(end - overlap, 0)
    return chunks


def score_sentence_relevance(query: str, sentence: str) -> float:
    query_terms = Counter(re.findall(r"\w+", query.lower()))
    sentence_terms = Counter(re.findall(r"\w+", sentence.lower()))
    shared = sum(min(query_terms[token], sentence_terms[token]) for token in query_terms)
    density = shared / max(sum(query_terms.values()), 1)
    return density + (0.15 * max(compute_sentiment(sentence), 0))


def top_sentences(query: str, text: str, limit: int = 4) -> list[str]:
    sentences = re.split(r"(?<=[.!?])\s+", text)
    ranked = sorted(
        (sentence.strip() for sentence in sentences if sentence.strip()),
        key=lambda sentence: score_sentence_relevance(query, sentence),
        reverse=True,
    )
    return ranked[:limit] or [text[:280]]


def extract_risks_and_opportunities(texts: list[str]) -> tuple[list[str], list[str]]:
    risks: list[str] = []
    opportunities: list[str] = []
    for sentence in texts:
        lowered = sentence.lower()
        if any(term in lowered for term in RISK_TERMS):
            risks.append(sentence)
        if any(term in lowered for term in OPPORTUNITY_TERMS):
            opportunities.append(sentence)
    return risks[:4], opportunities[:4]


def recency_score(published_at: str) -> float:
    delta_days = max((datetime.now(UTC) - parse_datetime(published_at)).days, 0)
    return float(np.exp(-(delta_days / 7)))
