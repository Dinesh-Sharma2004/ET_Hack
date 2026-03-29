from fastapi import FastAPI
from pydantic import BaseModel

from myet_shared.briefing import BriefingComposer
from myet_shared.repository import SharedRepository
from myet_shared.retrieval import HybridRetriever


class RagQueryRequest(BaseModel):
    query: str
    top_k: int = 5


class BriefingRequest(BaseModel):
    question: str
    mode: str = "expert"
    history: list[str] = []


repository = SharedRepository()
retriever = HybridRetriever()
composer = BriefingComposer()
app = FastAPI(title="MyET RAG Service", version="2.0.0")


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "service": "rag-service"}


@app.post("/rag/query")
async def query_rag(payload: RagQueryRequest) -> dict[str, object]:
    articles = repository.load_articles()
    hits = retriever.retrieve(payload.query, articles, top_k=payload.top_k)
    return {
        "query": payload.query,
        "strategy": "hybrid-faiss-semantic-keyword",
        "results": [hit.model_dump() for hit in hits],
    }


@app.get("/briefing/{topic}")
async def get_briefing(topic: str) -> dict[str, object]:
    articles = repository.search_articles(interest=topic, search=topic) or repository.load_articles()
    hits = retriever.retrieve(topic, articles, top_k=6)
    return composer.compose(topic, hits, {article.id: article for article in articles})


@app.post("/briefing/{topic}/chat")
async def briefing_chat(topic: str, payload: BriefingRequest) -> dict[str, object]:
    articles = repository.load_articles()
    hits = retriever.retrieve(payload.question or topic, articles, top_k=4)
    return composer.answer(topic, payload.question or topic, hits, {article.id: article for article in articles})
