from typing import List
import math
import re


def _tokenize(text: str) -> List[str]:
    return re.findall(r"[a-z0-9]+", (text or "").lower())


def simple_text_embedding(text: str, dim: int = 256) -> List[float]:
    """Lightweight local embedding to avoid external dependency.
    Stable, deterministic hash-based vector in [0,1].
    """
    vec = [0.0] * dim
    for tok in _tokenize(text):
        h = hash(tok)
        idx = abs(h) % dim
        val = (abs(h) % 1000) / 1000.0
        vec[idx] += val
    # L2 normalize
    norm = math.sqrt(sum(v * v for v in vec)) or 1.0
    return [v / norm for v in vec]


def cosine_similarity(a: List[float], b: List[float]) -> float:
    if not a or not b or len(a) != len(b):
        return 0.0
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a)) or 1.0
    nb = math.sqrt(sum(y * y for y in b)) or 1.0
    return dot / (na * nb)


