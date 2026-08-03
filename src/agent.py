"""
src/agent.py — Knowledge Base RAG Agent.

Retrieval-Augmented Generation (RAG) agent that queries an EmbeddingStore
for relevant context and prompts an LLM function to generate answers.
"""

from __future__ import annotations

from typing import Callable

from src.log import get_logger
from src.store import EmbeddingStore

logger = get_logger("agent")


class KnowledgeBaseAgent:
    """
    An agent that answers questions using a vector knowledge base.

    Retrieval-augmented generation (RAG) pattern:
        1. Retrieve top-k relevant chunks from the store using store.search().
        2. Build a prompt with formatted numbered context chunks for grounding.
        3. Call the LLM function to generate an answer.
    """

    def __init__(self, store: EmbeddingStore, llm_fn: Callable[[str], str]) -> None:
        self.store = store
        self.llm_fn = llm_fn

    def answer(self, question: str, top_k: int = 3) -> str:
        """
        Generate an answer for the given question using RAG.

        Args:
            question: User question string.
            top_k: Number of relevant chunks to retrieve.

        Returns:
            Generated answer string or empty store message.
        """
        if self.store.get_collection_size() == 0:
            logger.info("Store is empty. Returning default empty store message.")
            return "Cơ sở tri thức hiện chưa có dữ liệu để trả lời câu hỏi."

        logger.info(f"Retrieving top-{top_k} relevant chunk(s) for question: '{question}'")
        retrieved_chunks = self.store.search(question, top_k=top_k)

        # Build numbered grounding context
        context_parts = []
        for idx, chunk in enumerate(retrieved_chunks, start=1):
            meta = chunk.get("metadata", {})
            doc_id = meta.get("doc_id", "unknown")
            source = meta.get("source") or meta.get("source_url") or "N/A"
            chunk_idx = meta.get("chunk_index", "N/A")
            content = chunk.get("content", "").strip()

            header = f"[{idx}] doc_id: {doc_id} | source: {source} | chunk_index: {chunk_idx}"
            context_parts.append(f"{header}\n{content}")

        context_str = "\n\n".join(context_parts)

        prompt = (
            "Bạn là một trợ lý AI thông minh. Hãy trả lời câu hỏi của người dùng dựa TRỰC TIẾP và CHỈ dựa trên phần Context được cung cấp dưới đây.\n"
            "Nếu phần Context không chứa đủ thông tin để trả lời câu hỏi, hãy nói rõ rằng bạn không đủ thông tin để trả lời dựa trên tài liệu.\n\n"
            "Context:\n"
            f"{context_str}\n\n"
            f"Question: {question}\n\n"
            "Answer:"
        )

        logger.info("Generating answer from LLM...")
        return self.llm_fn(prompt)
