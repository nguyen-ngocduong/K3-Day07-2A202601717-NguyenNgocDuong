"""
src/chunking.py — Text Chunking Strategies and Similarity Utilities for RAG.

Provides multiple chunking strategies:
    - FixedSizeChunker: Sliding window fixed-length text chunker.
    - SentenceChunker: Sentence-boundary chunker using regex split.
    - RecursiveChunker: Priority-separator recursive chunker.
    - ChunkingStrategyComparator: Comparative analysis tool across strategies.

Also provides vector utility:
    - compute_similarity: Cosine similarity calculation.
"""

from __future__ import annotations

import json
import math
import re
from pathlib import Path

from src.log import get_logger
from src.models import Document

logger = get_logger("chunking")


class FixedSizeChunker:
    """
    Split text into fixed-size chunks with optional overlap.

    Rules:
        - Each chunk is at most chunk_size characters long.
        - Consecutive chunks share overlap characters.
        - The last chunk contains whatever remains.
        - If text is shorter than chunk_size, return [text].
    """

    def __init__(self, chunk_size: int = 500, overlap: int = 50) -> None:
        self.chunk_size = chunk_size
        self.overlap = overlap

    def chunk(self, text: str) -> list[str]:
        if not text:
            return []
        if len(text) <= self.chunk_size:
            return [text]

        step = max(1, self.chunk_size - self.overlap)
        chunks: list[str] = []
        for start in range(0, len(text), step):
            chunk_str = text[start : start + self.chunk_size]
            chunks.append(chunk_str)
            if start + self.chunk_size >= len(text):
                break
        return chunks


class SentenceChunker:
    """
    Split text into chunks of at most max_sentences_per_chunk sentences.

    Sentence detection uses regex lookbehind `r"(?<=[.!?])\s+"` to preserve punctuation.
    """

    def __init__(self, max_sentences_per_chunk: int = 3) -> None:
        self.max_sentences_per_chunk = max(1, max_sentences_per_chunk)

    def chunk(self, text: str) -> list[str]:
        if not text or not text.strip():
            return []

        # Split sentences preserving punctuation via lookbehind
        raw_sentences = re.split(r"(?<=[.!?])\s+", text)
        sentences = [s.strip() for s in raw_sentences if s.strip()]

        if not sentences:
            return []

        chunks: list[str] = []
        for i in range(0, len(sentences), self.max_sentences_per_chunk):
            group = sentences[i : i + self.max_sentences_per_chunk]
            chunk_str = " ".join(group).strip()
            if chunk_str:
                chunks.append(chunk_str)

        return chunks


class RecursiveChunker:
    """
    Recursively split text using separators in priority order.

    Default separator priority:
        ["\n\n", "\n", ". ", " ", ""]
    """

    DEFAULT_SEPARATORS = ["\n\n", "\n", ". ", " ", ""]

    def __init__(self, separators: list[str] | None = None, chunk_size: int = 500) -> None:
        self.separators = self.DEFAULT_SEPARATORS if separators is None else list(separators)
        self.chunk_size = chunk_size

    def chunk(self, text: str) -> list[str]:
        if not text:
            return []
        if len(text) <= self.chunk_size:
            return [text]

        return self._split(text, self.separators)

    def _split(self, current_text: str, remaining_separators: list[str]) -> list[str]:
        if not current_text:
            return []

        if len(current_text) <= self.chunk_size:
            return [current_text]

        if not remaining_separators:
            # Fallback to fixed size chunking when out of separators
            return FixedSizeChunker(chunk_size=self.chunk_size, overlap=0).chunk(current_text)

        separator = remaining_separators[0]
        next_separators = remaining_separators[1:]

        if separator == "":
            return FixedSizeChunker(chunk_size=self.chunk_size, overlap=0).chunk(current_text)

        splits = current_text.split(separator)
        if len(splits) <= 1:
            # Separator not present, try next separator
            return self._split(current_text, next_separators)

        chunks: list[str] = []
        current_chunk_parts: list[str] = []
        current_len = 0

        for part in splits:
            if not part and separator != "\n":
                continue

            part_len = len(part)
            sep_len = len(separator)

            # If an individual part exceeds chunk_size, split it with next separators
            if part_len > self.chunk_size:
                if current_chunk_parts:
                    chunks.append(separator.join(current_chunk_parts))
                    current_chunk_parts = []
                    current_len = 0

                sub_chunks = self._split(part, next_separators)
                chunks.extend(sub_chunks)
                continue

            added_len = part_len + (sep_len if current_chunk_parts else 0)
            if current_len + added_len <= self.chunk_size:
                current_chunk_parts.append(part)
                current_len += added_len
            else:
                if current_chunk_parts:
                    chunks.append(separator.join(current_chunk_parts))
                current_chunk_parts = [part]
                current_len = part_len

        if current_chunk_parts:
            chunks.append(separator.join(current_chunk_parts))

        return [c for c in chunks if c]


def _dot(a: list[float], b: list[float]) -> float:
    """Compute dot product of two numerical vectors."""
    return sum(x * y for x, y in zip(a, b))


def compute_similarity(vec_a: list[float], vec_b: list[float]) -> float:
    """
    Compute cosine similarity between two vectors.

    cosine_similarity = dot(a, b) / (||a|| * ||b||)

    Returns 0.0 if either vector has zero magnitude.
    """
    if not vec_a or not vec_b or len(vec_a) != len(vec_b):
        return 0.0

    mag_a = math.sqrt(sum(x * x for x in vec_a))
    mag_b = math.sqrt(sum(y * y for y in vec_b))

    if mag_a == 0.0 or mag_b == 0.0:
        return 0.0

    return _dot(vec_a, vec_b) / (mag_a * mag_b)


class ChunkingStrategyComparator:
    """Run all built-in chunking strategies and compare their results."""

    def compare(self, text: str, chunk_size: int = 200) -> dict:
        if not text or not text.strip():
            return {
                "fixed_size": {"count": 0, "avg_length": 0.0, "chunks": []},
                "by_sentences": {"count": 0, "avg_length": 0.0, "chunks": []},
                "recursive": {"count": 0, "avg_length": 0.0, "chunks": []},
            }

        fixed_chunker = FixedSizeChunker(chunk_size=chunk_size, overlap=20)
        sentence_chunker = SentenceChunker(max_sentences_per_chunk=3)
        recursive_chunker = RecursiveChunker(chunk_size=chunk_size)

        fixed_chunks = fixed_chunker.chunk(text)
        sentence_chunks = sentence_chunker.chunk(text)
        recursive_chunks = recursive_chunker.chunk(text)

        def _calc_stats(chunks: list[str]) -> dict:
            count = len(chunks)
            avg_length = sum(len(c) for c in chunks) / count if count > 0 else 0.0
            return {
                "count": count,
                "avg_length": avg_length,
                "chunks": chunks,
            }

        return {
            "fixed_size": _calc_stats(fixed_chunks),
            "by_sentences": _calc_stats(sentence_chunks),
            "recursive": _calc_stats(recursive_chunks),
        }


class HeadingChunker:
    """
    Domain-specific chunker for university policy documents.
    Splits text by markdown headings (#, ##, ###) first to preserve section context,
    then uses RecursiveChunker to further split large sections if needed.
    """

    def __init__(self, chunk_size: int = 500) -> None:
        self.chunk_size = chunk_size
        self.recursive_chunker = RecursiveChunker(chunk_size=chunk_size)

    def chunk(self, text: str) -> list[str]:
        if not text or not text.strip():
            return []

        # Split text by headings (#, ##, ###)
        heading_pattern = r"(?=\n#{1,4}\s+)"
        sections = [s.strip() for s in re.split(heading_pattern, text) if s.strip()]

        final_chunks: list[str] = []
        for sec in sections:
            if len(sec) <= self.chunk_size:
                final_chunks.append(sec)
            else:
                # Sub-split large sections while retaining heading prefix if possible
                lines = sec.splitlines()
                heading_prefix = lines[0] if lines[0].startswith("#") else ""
                sub_chunks = self.recursive_chunker.chunk(sec)
                for sc in sub_chunks:
                    if heading_prefix and not sc.startswith("#"):
                        sc = f"{heading_prefix}\n{sc}"
                    final_chunks.append(sc)

        return final_chunks


# =====================================================================
# Real Data Integration Pipeline Functions
# =====================================================================


def process_document_to_chunks(
    doc: Document,
    chunker=None,
) -> list[Document]:
    """
    Chunk a single Document into a list of chunk Documents with merged metadata.

    Metadata includes:
        - All original document metadata
        - source
        - chunk_index
        - total_chunks
    """
    chunker = chunker or FixedSizeChunker()
    raw_chunks = chunker.chunk(doc.content)
    total_chunks = len(raw_chunks)

    chunk_docs: list[Document] = []
    source_val = doc.metadata.get("source") or doc.metadata.get("source_url") or doc.id

    for idx, piece in enumerate(raw_chunks):
        meta = dict(doc.metadata)
        meta["source"] = source_val
        meta["chunk_index"] = idx
        meta["total_chunks"] = total_chunks
        meta["doc_id"] = doc.id

        chunk_doc = Document(
            id=f"{doc.id}::chunk_{idx}",
            content=piece,
            metadata=meta,
        )
        chunk_docs.append(chunk_doc)

    return chunk_docs


def process_chunking_directory(
    input_dir: Path = Path("data/k3_university_clean"),
    output_dir: Path = Path("data/k3_university_chunks"),
    chunker=None,
) -> tuple[int, int, float]:
    """
    Process all clean text documents in input_dir, generate chunk Documents,
    and save debug JSON files to output_dir.

    Returns:
        Tuple of (documents_processed, total_chunks, avg_chunks_per_doc).
    """
    from ingest import load_documents  # Use existing project loader

    chunker = chunker or FixedSizeChunker()

    if not input_dir.exists():
        logger.error(f"Input directory does not exist: {input_dir}")
        return (0, 0, 0.0)

    docs = load_documents(input_dir)
    total_docs = len(docs)
    total_chunks = 0

    output_dir.mkdir(parents=True, exist_ok=True)

    logger.info(f"Starting chunking pipeline on {total_docs} document(s) from {input_dir}")

    for doc in docs:
        logger.info(f"Processing file {doc.metadata.get('source', doc.id)}...")

        chunk_docs = process_document_to_chunks(doc, chunker)
        num_chunks = len(chunk_docs)
        total_chunks += num_chunks

        avg_len = (
            sum(len(c.content) for c in chunk_docs) / num_chunks
            if num_chunks > 0
            else 0.0
        )

        logger.info(f"Number of chunks: {num_chunks}")
        logger.info(f"Average chunk length: {avg_len:.1f}")

        # Save to output_dir for debugging
        def _json_default(obj):
            if hasattr(obj, "isoformat"):
                return obj.isoformat()
            return str(obj)

        debug_data = [
            {
                "id": c.id,
                "content": c.content,
                "metadata": c.metadata,
            }
            for c in chunk_docs
        ]
        out_file = output_dir / f"{doc.id}_chunks.json"
        out_file.write_text(
            json.dumps(debug_data, ensure_ascii=False, indent=2, default=_json_default),
            encoding="utf-8",
        )

    avg_chunks_per_doc = total_chunks / total_docs if total_docs > 0 else 0.0

    logger.info("Done")
    logger.info("=" * 50)
    logger.info("Chunking Pipeline Summary:")
    logger.info(f"  Documents processed: {total_docs}")
    logger.info(f"  Total chunks: {total_chunks}")
    logger.info(f"  Average chunks/document: {avg_chunks_per_doc:.2f}")
    logger.info("=" * 50)

    return (total_docs, total_chunks, avg_chunks_per_doc)


if __name__ == "__main__":
    process_chunking_directory()
