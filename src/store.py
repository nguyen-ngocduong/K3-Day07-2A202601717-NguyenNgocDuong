"""
src/store.py — Vector Store for Document Chunks in RAG System.

Supports in-memory storage (and modular backend extension) with:
    - Metadata pre-filtering
    - Cosine similarity ranking
    - Document chunk deletion
"""

from __future__ import annotations

import copy
from typing import Any, Callable

from src.chunking import compute_similarity, _dot
from src.embeddings import _mock_embed
from src.log import get_logger
from src.models import Document

logger = get_logger("store")


class EmbeddingStore:
    """
    A vector store for text chunks.

    Maintains stored records containing embeddings, content, and metadata.
    Supports similarity search, metadata pre-filtering, and document deletion.
    """

    def __init__(
        self,
        collection_name: str = "documents",
        embedding_fn: Callable[[str], list[float]] | None = None,
    ) -> None:
        self._embedding_fn = embedding_fn or _mock_embed
        self._collection_name = collection_name
        self._use_chroma = False
        self._store: list[dict[str, Any]] = []
        self._collection = None
        self._next_index = 0

        try:
            import chromadb  # noqa: F401

            # Future ChromaDB backend integration placeholder
            self._use_chroma = False
        except Exception:
            self._use_chroma = False
            self._collection = None

    def _make_record(self, doc: Document) -> dict[str, Any]:
        """
        Build a normalized stored record for one document chunk.

        Ensures metadata is safely copied and doc_id is present.
        Generates embedding using system's embedding_fn.
        """
        meta_copy = copy.deepcopy(doc.metadata) if doc.metadata else {}
        doc_id = meta_copy.get("doc_id") or doc.id
        meta_copy["doc_id"] = doc_id

        # Generate embedding for content
        embedding = self._embedding_fn(doc.content)

        record_id = doc.id or f"chunk_{self._next_index}"
        self._next_index += 1

        return {
            "id": record_id,
            "content": doc.content,
            "metadata": meta_copy,
            "embedding": embedding,
        }

    def _search_records(
        self, query: str, records: list[dict[str, Any]], top_k: int
    ) -> list[dict[str, Any]]:
        """
        Run similarity search over provided records for a given query string.

        Embeds query once, calculates similarity score, and returns top_k results.
        """
        if not records or top_k <= 0:
            return []

        logger.info(f"Searching top-{top_k} results across {len(records)} candidate record(s)")
        query_embedding = self._embedding_fn(query)

        scored_results: list[dict[str, Any]] = []
        for rec in records:
            rec_embedding = rec.get("embedding", [])
            score = compute_similarity(query_embedding, rec_embedding)

            scored_results.append({
                "id": rec["id"],
                "content": rec["content"],
                "metadata": copy.deepcopy(rec["metadata"]),
                "score": score,
            })

        # Sort descending by similarity score
        scored_results.sort(key=lambda x: x["score"], reverse=True)

        return scored_results[:top_k]

    def add_documents(self, docs: list[Document]) -> None:
        """
        Embed each document's content and store it.

        For in-memory: append generated records to self._store.
        Safely ignores empty document lists.
        """
        if not docs:
            logger.info("add_documents called with empty list. Skipping.")
            return

        logger.info(f"Indexing {len(docs)} document chunk(s) into store '{self._collection_name}'...")
        for doc in docs:
            record = self._make_record(doc)
            self._store.append(record)

        logger.info(f"Total stored chunks now: {len(self._store)}")

    def search(self, query: str, top_k: int = 5) -> list[dict[str, Any]]:
        """Find the top_k most similar documents to query."""
        return self._search_records(query, self._store, top_k)

    def get_collection_size(self) -> int:
        """Return the total number of stored chunks."""
        return len(self._store)

    def search_with_filter(
        self, query: str, top_k: int = 3, metadata_filter: dict | None = None
    ) -> list[dict[str, Any]]:
        """
        Search with metadata pre-filtering.

        First filters stored chunks by metadata_filter, then runs similarity search.
        If metadata_filter is None or empty, behaves identically to search().
        """
        if not metadata_filter:
            return self.search(query, top_k)

        # Pre-filter records matching all key-value pairs in metadata_filter
        filtered_records = []
        for rec in self._store:
            rec_meta = rec.get("metadata", {})
            match = True
            for key, val in metadata_filter.items():
                if rec_meta.get(key) != val:
                    match = False
                    break
            if match:
                filtered_records.append(rec)

        logger.info(
            f"Metadata filter {metadata_filter} matched {len(filtered_records)}/{len(self._store)} records"
        )
        return self._search_records(query, filtered_records, top_k)

    def delete_document(self, doc_id: str) -> bool:
        """
        Remove all stored chunks belonging to a document (metadata['doc_id'] == doc_id).

        Returns True if any chunks were removed, False otherwise.
        """
        initial_count = len(self._store)
        self._store = [
            rec for rec in self._store if rec.get("metadata", {}).get("doc_id") != doc_id
        ]
        removed_count = initial_count - len(self._store)

        if removed_count > 0:
            logger.info(f"Deleted {removed_count} chunk(s) for doc_id='{doc_id}'")
            return True

        logger.info(f"No chunks found for doc_id='{doc_id}' to delete")
        return False
