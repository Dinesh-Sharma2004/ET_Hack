from functools import lru_cache

from transformers import AutoModelForSeq2SeqLM, AutoTokenizer


GENERATION_MODEL = "google/flan-t5-small"


@lru_cache(maxsize=1)
def _load_generator():
    tokenizer = AutoTokenizer.from_pretrained(GENERATION_MODEL)
    model = AutoModelForSeq2SeqLM.from_pretrained(GENERATION_MODEL)
    return tokenizer, model


def generate_text(prompt: str, max_new_tokens: int = 160) -> str:
    tokenizer, model = _load_generator()
    encoded = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=512)
    generated = model.generate(**encoded, max_new_tokens=max_new_tokens)
    return tokenizer.batch_decode(generated, skip_special_tokens=True)[0].strip()
