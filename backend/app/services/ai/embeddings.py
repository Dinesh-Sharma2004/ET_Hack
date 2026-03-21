from collections import Counter

import numpy as np


def embed_text(text: str) -> np.ndarray:
    tokens = [token.strip(".,:;!?").lower() for token in text.split() if token.strip()]
    counts = Counter(tokens)
    vocab = sorted(counts)
    return np.array([counts[token] / max(len(tokens), 1) for token in vocab], dtype=float)


def cosine_similarity(left: np.ndarray, right: np.ndarray) -> float:
    if left.size == 0 or right.size == 0:
        return 0.0
    all_tokens = max(left.size, right.size)
    left_resized = np.pad(left, (0, all_tokens - left.size))
    right_resized = np.pad(right, (0, all_tokens - right.size))
    denominator = np.linalg.norm(left_resized) * np.linalg.norm(right_resized)
    if denominator == 0:
        return 0.0
    return float(np.dot(left_resized, right_resized) / denominator)
