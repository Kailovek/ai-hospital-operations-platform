import hashlib
import math
import re
from collections import Counter
from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import KnowledgeChunk, KnowledgeDocument
from app.modules.knowledge.schemas import SearchHit

LATIN_TOKEN_PATTERN = re.compile(r"[a-zA-Z0-9_-]+")
CJK_SEQUENCE_PATTERN = re.compile(r"[\u3400-\u4dbf\u4e00-\u9fff]+")
VECTOR_SIZE = 128


def tokenize(text: str) -> list[str]:
    tokens = [token.lower() for token in LATIN_TOKEN_PATTERN.findall(text)]
    for sequence in CJK_SEQUENCE_PATTERN.findall(text):
        if len(sequence) == 1:
            tokens.append(sequence)
        else:
            tokens.extend(sequence[index : index + 2] for index in range(len(sequence) - 1))
    return tokens


def deterministic_embedding(text: str) -> list[float]:
    vector = [0.0] * VECTOR_SIZE
    for token in tokenize(text):
        digest = hashlib.sha256(token.encode("utf-8")).digest()
        index = int.from_bytes(digest[:2], "big") % VECTOR_SIZE
        sign = 1.0 if digest[2] % 2 == 0 else -1.0
        vector[index] += sign
    norm = math.sqrt(sum(value * value for value in vector)) or 1.0
    return [value / norm for value in vector]


def cosine(left: list[float], right: list[float]) -> float:
    return sum(a * b for a, b in zip(left, right, strict=True))


@dataclass
class Candidate:
    chunk: KnowledgeChunk
    document: KnowledgeDocument
    dense_score: float
    keyword_score: float
    fusion_score: float = 0.0
    rerank_score: float = 0.0


def search(db: Session, query: str, top_k: int) -> list[SearchHit]:
    rows = db.execute(
        select(KnowledgeChunk, KnowledgeDocument).join(
            KnowledgeDocument, KnowledgeChunk.document_id == KnowledgeDocument.id
        )
    ).all()
    if not rows:
        return []
    query_tokens = tokenize(query)
    query_counts = Counter(query_tokens)
    query_vector = deterministic_embedding(query)
    document_frequency = Counter(
        token for chunk, _ in rows for token in set(tokenize(chunk.content))
    )
    candidates: list[Candidate] = []
    for chunk, document in rows:
        chunk_tokens = tokenize(chunk.content)
        counts = Counter(chunk_tokens)
        keyword = sum(
            query_counts[token]
            * counts[token]
            * math.log((len(rows) + 1) / (document_frequency[token] + 0.5))
            for token in query_counts
        )
        candidates.append(
            Candidate(
                chunk=chunk,
                document=document,
                dense_score=cosine(query_vector, deterministic_embedding(chunk.content)),
                keyword_score=keyword,
            )
        )

    dense_ranking = sorted(candidates, key=lambda item: item.dense_score, reverse=True)
    keyword_ranking = sorted(candidates, key=lambda item: item.keyword_score, reverse=True)
    for ranking in (dense_ranking, keyword_ranking):
        for rank, candidate in enumerate(ranking, 1):
            candidate.fusion_score += 1.0 / (60.0 + rank)

    query_set = set(query_tokens)
    for candidate in candidates:
        content_set = set(tokenize(candidate.chunk.content))
        overlap = len(query_set & content_set) / max(len(query_set), 1)
        candidate.rerank_score = candidate.fusion_score + overlap

    ranked = sorted(candidates, key=lambda item: item.rerank_score, reverse=True)[:top_k]
    return [
        SearchHit(
            chunk_id=candidate.chunk.id,
            document_id=candidate.document.id,
            title=candidate.document.title,
            content=candidate.chunk.content,
            score=round(candidate.rerank_score, 6),
            citation=f"[{candidate.document.title}#{candidate.chunk.ordinal + 1}]",
            scores={
                "dense_score": round(candidate.dense_score, 6),
                "keyword_score": round(candidate.keyword_score, 6),
                "fusion_score": round(candidate.fusion_score, 6),
                "rerank_score": round(candidate.rerank_score, 6),
            },
        )
        for candidate in ranked
    ]
