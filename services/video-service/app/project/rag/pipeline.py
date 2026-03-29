from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import requests
from bs4 import BeautifulSoup
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

from ..config import (
    CHROMA_COLLECTION,
    VIDEO_EMBED_ALLOW_DOWNLOADS,
    VIDEO_EMBED_LOCAL_ONLY_FIRST,
    VIDEO_EMBED_MODEL,
)
from ..utils import get_logger


logger = get_logger("myet.video.rag")


@dataclass
class LoadedNews:
    title: str
    text: str
    source: str
    url: str | None = None


class NewsRAGPipeline:
    def __init__(self) -> None:
        self._splitter = RecursiveCharacterTextSplitter(chunk_size=700, chunk_overlap=120)
        self._embeddings = None

    def load_source(self, *, text: str | None = None, url: str | None = None, pdf_path: str | None = None, title: str | None = None) -> LoadedNews:
        if url:
            return self._load_from_url(url)
        if pdf_path:
            return self._load_from_pdf(pdf_path, title=title)
        if text:
            guessed_title = title or text.split(".")[0][:100] or "Custom news brief"
            return LoadedNews(title=guessed_title, text=text.strip(), source="direct-text")
        raise ValueError("One of text, url, or pdf_path is required.")

    def build_context(self, loaded: LoadedNews, persist_dir: Path, query: str, top_k: int = 6) -> tuple[list[Document], list[str]]:
        persist_dir.mkdir(parents=True, exist_ok=True)
        documents = self._split_documents(loaded)
        try:
            embeddings = self._get_embeddings()
            vectorstore = Chroma.from_documents(
                documents=documents,
                embedding=embeddings,
                collection_name=CHROMA_COLLECTION,
                persist_directory=str(persist_dir),
            )
            matches = vectorstore.similarity_search(query=query, k=top_k)
        except Exception as exc:  # noqa: BLE001
            logger.warning("Embedding-backed retrieval unavailable, using local keyword fallback: %s", exc)
            matches = self._keyword_fallback(documents, query=query, top_k=top_k)
        context = [match.page_content for match in matches]
        logger.info("Retrieved %s chunks for video generation.", len(context))
        return matches, context

    def _split_documents(self, loaded: LoadedNews) -> list[Document]:
        base_document = Document(
            page_content=loaded.text,
            metadata={"title": loaded.title, "source": loaded.source, "url": loaded.url},
        )
        return self._splitter.split_documents([base_document])

    def _get_embeddings(self):
        if self._embeddings is not None:
            return self._embeddings
        attempts = []
        if VIDEO_EMBED_LOCAL_ONLY_FIRST:
            attempts.append(True)
        if VIDEO_EMBED_ALLOW_DOWNLOADS or not attempts:
            attempts.append(False)
        last_error = None
        for local_only in attempts:
            try:
                self._embeddings = HuggingFaceEmbeddings(
                    model_name=VIDEO_EMBED_MODEL,
                    model_kwargs={"local_files_only": local_only},
                )
                return self._embeddings
            except Exception as exc:  # noqa: BLE001
                last_error = exc
                logger.warning("Embedding initialization failed with local_only=%s: %s", local_only, exc)
        if last_error:
            raise last_error
        return self._embeddings

    @staticmethod
    def _keyword_fallback(documents: list[Document], query: str, top_k: int) -> list[Document]:
        query_terms = {term for term in query.lower().split() if len(term) > 2}
        ranked = []
        for document in documents:
            content = document.page_content.lower()
            score = sum(content.count(term) for term in query_terms)
            ranked.append((score, document))
        ranked.sort(key=lambda item: item[0], reverse=True)
        selected = [document for _, document in ranked[:top_k] if document.page_content.strip()]
        return selected or documents[:top_k]

    def _load_from_url(self, url: str) -> LoadedNews:
        response = requests.get(
            url,
            timeout=30,
            headers={
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0 Safari/537.36"
                )
            },
        )
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        for tag in soup(["script", "style", "noscript"]):
            tag.decompose()
        title = soup.title.get_text(" ", strip=True) if soup.title else url
        paragraphs = [node.get_text(" ", strip=True) for node in soup.find_all("p")]
        body = "\n".join(line for line in paragraphs if len(line.split()) > 8)
        if not body:
            raise ValueError(f"Could not extract meaningful article text from {url}.")
        return LoadedNews(title=title, text=body, source="url", url=url)

    def _load_from_pdf(self, pdf_path: str, title: str | None = None) -> LoadedNews:
        try:
            import fitz
        except ImportError as exc:
            raise ValueError("PDF ingestion requires PyMuPDF, which is not installed in this runtime.") from exc
        pdf = fitz.open(pdf_path)
        text = "\n".join(page.get_text("text") for page in pdf)
        pdf.close()
        if not text.strip():
            raise ValueError(f"PDF {pdf_path} did not contain readable text.")
        return LoadedNews(title=title or Path(pdf_path).stem, text=text, source="pdf")
