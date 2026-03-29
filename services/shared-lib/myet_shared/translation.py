from __future__ import annotations

import hashlib
import json
import logging
from functools import lru_cache
from pathlib import Path

from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

from myet_shared.config import (
    TRANSLATION_ALLOW_DOWNLOADS,
    TRANSLATION_CACHE_DIR,
    TRANSLATION_LOCAL_ONLY_FIRST,
    TRANSLATION_MODEL_BN,
    TRANSLATION_MODEL_HI,
    TRANSLATION_MODEL_TA,
    TRANSLATION_MODEL_TE,
)
from myet_shared.models import Article


logger = logging.getLogger("myet.translation")

MODEL_MAP = {
    "Hindi": ("marian", TRANSLATION_MODEL_HI),
    "Bengali": ("marian", TRANSLATION_MODEL_BN),
    "Tamil": ("mbart", TRANSLATION_MODEL_TA),
    "Telugu": ("mbart", TRANSLATION_MODEL_TE),
}

MBART_LANGUAGE_CODES = {
    "Tamil": "ta_IN",
    "Telugu": "te_IN",
}


@lru_cache(maxsize=8)
def _load_model_bundle(language: str, local_only: bool):
    family, model_name = MODEL_MAP.get(language, MODEL_MAP["Hindi"])
    tokenizer = AutoTokenizer.from_pretrained(model_name, local_files_only=local_only)
    model = AutoModelForSeq2SeqLM.from_pretrained(model_name, local_files_only=local_only)
    model.eval()
    return family, tokenizer, model


def _resolve_model(language: str):
    attempts = []
    if TRANSLATION_LOCAL_ONLY_FIRST:
        attempts.append(True)
    if TRANSLATION_ALLOW_DOWNLOADS or not attempts:
        attempts.append(False)

    last_error = None
    for local_only in attempts:
        try:
            return _load_model_bundle(language, local_only)
        except Exception as exc:  # noqa: BLE001
            last_error = exc
            logger.warning(
                "Translation model load failed for %s with local_only=%s: %s",
                language,
                local_only,
                exc,
            )
    raise RuntimeError(f"Unable to load translation model for {language}.") from last_error


class VernacularEngine:
    def translate(self, article: Article, language: str, mode: str = "contextual") -> dict[str, str]:
        cache_path = self._cache_path(article, language, mode)
        if cache_path.exists():
            return json.loads(cache_path.read_text(encoding="utf-8"))

        family, tokenizer, model = _resolve_model(language)
        source_text = self._build_source_text(article, mode)

        if family == "mbart":
            tokenizer.src_lang = "en_XX"
            encoded = tokenizer(source_text, return_tensors="pt", truncation=True, max_length=512)
            generated = model.generate(
                **encoded,
                forced_bos_token_id=tokenizer.lang_code_to_id[MBART_LANGUAGE_CODES.get(language, "hi_IN")],
                max_new_tokens=220,
            )
        else:
            encoded = tokenizer(source_text, return_tensors="pt", truncation=True, max_length=512)
            generated = model.generate(**encoded, max_new_tokens=220)

        content = tokenizer.batch_decode(generated, skip_special_tokens=True)[0]
        payload = {
            "article_id": article.id,
            "language": language,
            "mode": mode,
            "title": article.title,
            "content": content,
        }
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        cache_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        return payload

    def warm_models(self, languages: list[str]) -> None:
        for language in languages:
            try:
                _resolve_model(language)
                logger.info("Translation model warmed for %s", language)
            except Exception as exc:  # noqa: BLE001
                logger.warning("Translation warmup failed for %s: %s", language, exc)

    def _cache_path(self, article: Article, language: str, mode: str) -> Path:
        fingerprint = hashlib.sha1(
            json.dumps(
                {
                    "article_id": article.id,
                    "title": article.title,
                    "summary": article.summary,
                    "content": article.content[:800],
                    "language": language,
                    "mode": mode,
                },
                sort_keys=True,
                ensure_ascii=False,
            ).encode("utf-8")
        ).hexdigest()
        return TRANSLATION_CACHE_DIR / language.lower() / f"{fingerprint}.json"

    def _build_source_text(self, article: Article, mode: str) -> str:
        if mode == "literal":
            return self._literal_text(article)
        return self._contextual_english_text(article)

    @staticmethod
    def _literal_text(article: Article) -> str:
        body = article.summary if len(article.summary.split()) > 12 else article.content
        return f"{article.title}. {body}".strip()

    @staticmethod
    def _contextual_english_text(article: Article) -> str:
        audience_map = {
            "Markets": "investors and traders",
            "Mutual Funds": "long-term investors and savers",
            "Startups": "startup founders and operators",
            "Technology": "technology leaders and founders",
            "Business": "business leaders and investors",
            "Energy": "energy buyers, companies, and market watchers",
        }
        audience = audience_map.get(article.category, "business readers in India")
        entities = ", ".join(article.entities[:4])
        why_it_matters = (
            f"This matters for {audience} because it can influence prices, investment decisions, "
            f"company strategy, and near-term business sentiment."
        )
        if entities:
            why_it_matters += f" The main names in focus are {entities}."
        return (
            f"{article.title}. "
            f"{article.summary}. "
            f"{why_it_matters}"
        ).strip()
