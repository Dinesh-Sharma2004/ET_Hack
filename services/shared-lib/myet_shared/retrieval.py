import json
import re
from hashlib import sha1

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

from myet_shared.config import EMBEDDING_MODEL, VECTOR_DIR
from myet_shared.models import Article, RetrievalHit
from myet_shared.nlp import chunk_text


INDEX_PATH = VECTOR_DIR / "articles.faiss"
METADATA_PATH = VECTOR_DIR / "articles.metadata.json"


class HybridRetriever:
    def __init__(self) -> None:
        self.model = SentenceTransformer(EMBEDDING_MODEL)

    def retrieve(self, query: str, articles: list[Article], top_k: int = 5) -> list[RetrievalHit]:
        metadata = self._sync_index(articles)
        if not metadata:
            return []

        index = faiss.read_index(str(INDEX_PATH))
        query_vector = self.model.encode([query], normalize_embeddings=True).astype("float32")
        distances, indices = index.search(query_vector, min(top_k * 3, len(metadata)))
        query_terms = set(re.findall(r"\w+", query.lower()))
        hits: list[RetrievalHit] = []

        for rank, metadata_index in enumerate(indices[0]):
            if metadata_index < 0:
                continue
            item = metadata[metadata_index]
            keyword_terms = set(re.findall(r"\w+", item["text"].lower()))
            keyword_overlap = len(query_terms & keyword_terms) / max(len(query_terms), 1)
            dense_score = float(distances[0][rank])
            combined = round((dense_score * 0.75) + (keyword_overlap * 0.25), 4)
            hits.append(
                RetrievalHit(
                    article_id=item["article_id"],
                    title=item["title"],
                    chunk_id=item["chunk_id"],
                    text=item["text"],
                    dense_score=round(dense_score, 4),
                    keyword_score=round(keyword_overlap, 4),
                    combined_score=combined,
                    source=item.get("source"),
                    published_at=item.get("published_at"),
                    url=item.get("url"),
                )
            )

        deduped: dict[str, RetrievalHit] = {}
        for hit in sorted(hits, key=lambda item: item.combined_score, reverse=True):
            deduped.setdefault(hit.chunk_id, hit)
        return list(deduped.values())[:top_k]

    def _sync_index(self, articles: list[Article]) -> list[dict]:
        chunks: list[dict] = []
        for article in articles:
            for position, chunk in enumerate(chunk_text(" ".join([article.title, article.summary, article.content]))):
                chunks.append(
                    {
                        "article_id": article.id,
                        "title": article.title,
                        "chunk_id": sha1(f"{article.id}:{position}:{chunk}".encode("utf-8")).hexdigest(),
                        "text": chunk,
                        "source": article.source,
                        "published_at": article.published_at,
                        "url": article.url,
                    }
                )
        if not chunks:
            return []

        digest = sha1(json.dumps(chunks, sort_keys=True).encode("utf-8")).hexdigest()
        if METADATA_PATH.exists() and INDEX_PATH.exists():
            existing = json.loads(METADATA_PATH.read_text(encoding="utf-8"))
            if existing.get("digest") == digest:
                return existing["items"]

        embeddings = self.model.encode([item["text"] for item in chunks], normalize_embeddings=True).astype("float32")
        index = faiss.IndexFlatIP(embeddings.shape[1])
        index.add(np.asarray(embeddings))
        faiss.write_index(index, str(INDEX_PATH))
        METADATA_PATH.write_text(json.dumps({"digest": digest, "items": chunks}, indent=2), encoding="utf-8")
        return chunks
