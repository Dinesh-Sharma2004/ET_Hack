from __future__ import annotations

import hashlib


def stable_hash(*parts: str) -> str:
    digest = hashlib.sha1()
    for part in parts:
        digest.update((part or "").encode("utf-8"))
        digest.update(b"|")
    return digest.hexdigest()
