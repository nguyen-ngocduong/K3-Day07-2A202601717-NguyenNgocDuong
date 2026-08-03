"""
bench.py — Benchmark Evaluation Module for Chunking Strategies in RAG.

Evaluates chunking strategies (FixedSizeChunker, SentenceChunker, RecursiveChunker, HeadingChunker)
fairly on the clean corpus `data/k3_university_clean` using `build_knowledge_base()` from `ingest.py`.

Runs 5 benchmark queries across 5 representation categories:
    1. Numerical Query (Truy vấn số liệu)
    2. Condition Query (Truy vấn điều kiện)
    3. Process Query (Truy vấn quy trình)
    4. Enumeration Query (Truy vấn liệt kê)
    5. Exception & Metadata Filter Query (Truy vấn ngoại lệ & lọc metadata)

Outputs benchmark reports to stdout, logs to `logs/app.log`, and generates a markdown summary report `report/BENCHMARK_RESULTS.md`.
"""

from __future__ import annotations

import os
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

from ingest import build_knowledge_base, load_documents
from src.agent import KnowledgeBaseAgent
from src.chunking import (
    FixedSizeChunker,
    HeadingChunker,
    RecursiveChunker,
    SentenceChunker,
)
from src.embeddings import (
    EMBEDDING_PROVIDER_ENV,
    LOCAL_EMBEDDING_MODEL,
    OPENAI_EMBEDDING_MODEL,
    LocalEmbedder,
    OpenAIEmbedder,
    _mock_embed,
)
from src.log import get_logger

logger = get_logger("benchmark")

DATA_CLEAN_DIR = Path("data/k3_university_clean")
REPORT_DIR = Path("report")
REPORT_FILE = REPORT_DIR / "BENCHMARK_RESULTS.md"


@dataclass
class BenchmarkQuery:
    id: str
    category: str
    question: str
    gold_answer: str
    expected_doc_id: str
    metadata_filter: dict[str, Any] | None = None


# Define 5 representative benchmark queries based on the K3 PTIT clean corpus
BENCHMARK_QUERIES: list[BenchmarkQuery] = [
    BenchmarkQuery(
        id="Q1_NUMERICAL",
        category="Truy vấn số liệu",
        question="Số lượng lớp học phần bị hủy do số lượng sinh viên đăng ký thời khóa biểu không đủ điều kiện mở lớp trong đợt học lại kỳ phụ năm 2025-2026 là bao nhiêu?",
        gold_answer="Hủy 16 lớp học phần do số lượng sinh viên đăng ký thời khóa biểu không đủ điều kiện mở lớp.",
        expected_doc_id="thong-bao-v-v-huy-cac-lop-hoc-phan-dot-hoc-lai-ky-phu-he-nam-hoc-2025-2026",
    ),
    BenchmarkQuery(
        id="Q2_CONDITION",
        category="Truy vấn điều kiện",
        question="Điều kiện để sinh viên đại học chính quy khóa 2024, 2025 được đăng ký lịch học theo tiến trình rút gọn học kỳ I năm học 2026-2027 là gì?",
        gold_answer="Sinh viên đã đăng ký nguyện vọng học theo tiến trình rút gọn, không được đăng ký các môn ngoài tiến trình rút gọn, không đăng ký học lại/học cải thiện trong thời gian này và phải đảm bảo các điều kiện tiên quyết của học phần.",
        expected_doc_id="dang-ky-lich-hoc-thoi-khoa-bieu-cho-sinh-vien-khoa-2024-2025-hoc-theo-tien-trinh-rut-gon-cua-hoc-ky-i-nam-hoc-2026-2027",
    ),
    BenchmarkQuery(
        id="Q3_PROCESS",
        category="Truy vấn quy trình",
        question="Quy trình các bước sinh viên thực hiện đăng ký nguyện vọng học vượt học kỳ I năm học 2026-2027 trên hệ thống QLĐT?",
        gold_answer="Bước 1: Đăng nhập Hệ thống QLĐT và chọn chức năng 'Đăng ký nguyện vọng'. Bước 2: Nhập mã học phần theo CTĐT học vượt đã được công bố. Bước 3: Nhấn nút 'Đăng ký' để lưu kết quả.",
        expected_doc_id="to-chuc-dang-ky-hoc-vuot-hoc-ky-i-nam-hoc-2026-2027-doi-voi-sinh-vien-khoa-2024-2025",
    ),
    BenchmarkQuery(
        id="Q4_ENUMERATION",
        category="Truy vấn liệt kê",
        question="Liệt kê danh sách các môn học bị hủy trong đợt học lại kỳ phụ (hè) năm học 2025-2026?",
        gold_answer="Tiếng Anh (Course 1 _CLC), Thị giác máy tính, Cơ sở đo lường điện tử, Truyền thông số, Marketing căn bản, Marketing công nghiệp, Nguyên lý kế toán, Xác suất thống kê, Toán rời rạc 2, Luật xa gần, CAD/CAM, Kiến trúc máy tính, Ngôn ngữ lập trình Java, Kỹ thuật quay phim, Kịch bản đa phương tiện, Vật lý 3 và thí nghiệm.",
        expected_doc_id="thong-bao-v-v-huy-cac-lop-hoc-phan-dot-hoc-lai-ky-phu-he-nam-hoc-2025-2026",
    ),
    BenchmarkQuery(
        id="Q5_FILTER_EXCEPTION",
        category="Truy vấn ngoại lệ & Metadata Filter",
        question="Thông tin dành riêng cho sinh viên (audience=student) về xử lý đối với sinh viên có học phần bị hủy do không đủ sĩ số?",
        gold_answer="Phòng Giáo vụ sẽ thực hiện hủy kết quả đăng ký của Sinh viên trên hệ thống, sinh viên không cần thực hiện thao tác hủy học phần hay làm Đơn đề nghị hủy.",
        expected_doc_id="thong-bao-v-v-huy-cac-lop-hoc-phan-dot-hoc-lai-ky-phu-he-nam-hoc-2025-2026",
        metadata_filter={"audience": "student", "department": "academic-affairs"},
    ),
]


def _select_embedder():
    """Select embedding backend according to EMBEDDING_PROVIDER environment variable."""
    provider = os.getenv(EMBEDDING_PROVIDER_ENV, "mock").strip().lower()
    if provider == "local":
        try:
            return LocalEmbedder(model_name=os.getenv("LOCAL_EMBEDDING_MODEL", LOCAL_EMBEDDING_MODEL))
        except Exception:
            logger.warning("Local embedder unavailable; falling back to _mock_embed.")
            return _mock_embed
    if provider == "openai":
        try:
            return OpenAIEmbedder(model_name=os.getenv("OPENAI_EMBEDDING_MODEL", OPENAI_EMBEDDING_MODEL))
        except Exception:
            logger.warning("OpenAI embedder unavailable; falling back to _mock_embed.")
            return _mock_embed
    return _mock_embed


def mock_llm_generator(prompt: str) -> str:
    """Deterministic mock LLM for benchmark comparison."""
    # Extract Context lines from prompt
    lines = prompt.splitlines()
    context_lines = [l for l in lines if l.startswith("[") and "doc_id:" in l]
    summary_sources = ", ".join(context_lines[:2])
    return f"[Agent Generated Answer based on Context]\nTrích dẫn nguồn: {summary_sources}."


def run_benchmark_for_strategy(
    strategy_name: str,
    chunker: Any,
    strategy_params: dict[str, Any],
    embedder: Callable[[str], list[float]],
) -> dict[str, Any]:
    """Run benchmark suite for a specific chunker strategy."""
    logger.info(f"\n" + "=" * 60)
    logger.info(f"RUNNING BENCHMARK STRATEGY: {strategy_name}")
    logger.info(f"Strategy Parameters: {strategy_params}")
    logger.info("=" * 60)

    start_index_time = time.perf_counter()

    # Step 1: Ingest using build_knowledge_base
    docs = load_documents(DATA_CLEAN_DIR)
    total_docs = len(docs)

    store = build_knowledge_base(
        data_dir=DATA_CLEAN_DIR,
        embedding_fn=embedder,
        chunker=chunker,
        collection_name=f"bench_{strategy_name.lower()}",
    )

    indexing_time = time.perf_counter() - start_index_time
    total_chunks = store.get_collection_size()
    avg_chunks_per_doc = total_chunks / total_docs if total_docs > 0 else 0.0

    # Calculate average chunk character length
    all_record_lens = [len(rec["content"]) for rec in store._store]
    avg_chunk_length = sum(all_record_lens) / len(all_record_lens) if all_record_lens else 0.0

    agent = KnowledgeBaseAgent(store=store, llm_fn=mock_llm_generator)

    query_results = []
    total_retrieval_time = 0.0

    for bq in BENCHMARK_QUERIES:
        logger.info(f"\n--- Benchmark Query [{bq.id}] ({bq.category}) ---")
        logger.info(f"Question: {bq.question}")
        if bq.metadata_filter:
            logger.info(f"Applying Metadata Filter: {bq.metadata_filter}")

        start_retrieval = time.perf_counter()

        if bq.metadata_filter:
            retrieved = store.search_with_filter(bq.question, top_k=3, metadata_filter=bq.metadata_filter)
        else:
            retrieved = store.search(bq.question, top_k=3)

        retrieval_time = time.perf_counter() - start_retrieval
        total_retrieval_time += retrieval_time

        agent_answer = agent.answer(bq.question, top_k=3)

        # Logging top-3 retrieval
        logger.info("Top-3 Retrieved Chunks:")
        top_k_summary = []
        for idx, res in enumerate(retrieved, start=1):
            score = res.get("score", 0.0)
            doc_id = res.get("metadata", {}).get("doc_id", "N/A")
            chunk_idx = res.get("metadata", {}).get("chunk_index", "N/A")
            source = res.get("metadata", {}).get("source", "N/A")
            preview = res.get("content", "").replace("\n", " ")[:180]

            logger.info(
                f"  [{idx}] score={score:.4f} | doc_id={doc_id} | chunk_idx={chunk_idx} | source={source}"
            )
            logger.info(f"      Preview: {preview}...")

            top_k_summary.append({
                "rank": idx,
                "score": score,
                "doc_id": doc_id,
                "chunk_index": chunk_idx,
                "preview": preview,
            })

        logger.info(f"Agent Answer: {agent_answer}")

        query_results.append({
            "query_id": bq.id,
            "category": bq.category,
            "question": bq.question,
            "metadata_filter": bq.metadata_filter,
            "retrieval_time_sec": retrieval_time,
            "retrieved_top_k": top_k_summary,
            "agent_answer": agent_answer,
        })

    return {
        "strategy_name": strategy_name,
        "strategy_params": strategy_params,
        "total_documents": total_docs,
        "total_chunks": total_chunks,
        "avg_chunks_per_doc": avg_chunks_per_doc,
        "avg_chunk_length": avg_chunk_length,
        "indexing_time_sec": indexing_time,
        "total_retrieval_time_sec": total_retrieval_time,
        "query_results": query_results,
    }


def generate_markdown_report(results: list[dict[str, Any]]) -> str:
    """Generate Markdown report table comparing all evaluated strategies."""
    report_lines = [
        "# Báo Cáo Đánh Giá So Sánh Chiến Lược Chunking (Benchmark Report)",
        "",
        f"> Được tạo tự động vào lúc: {time.strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        "## 1. Tổng Quan Hiệu Năng Các Chiến Lược",
        "",
        "| Chiến Lược (Strategy) | Kích Thước / Tham Số | Tổng Chunks | Avg Chunks/Doc | Độ Dài TB (chars) | Thời Gian Indexing (s) | Thời Gian Retrieval (s) |",
        "|---|---|---|---|---|---|---|",
    ]

    for res in results:
        param_str = ", ".join(f"{k}={v}" for k, v in res["strategy_params"].items())
        report_lines.append(
            f"| **{res['strategy_name']}** | `{param_str}` | {res['total_chunks']} | {res['avg_chunks_per_doc']:.2f} | {res['avg_chunk_length']:.1f} | {res['indexing_time_sec']:.4f}s | {res['total_retrieval_time_sec']:.4f}s |"
        )

    report_lines.extend([
        "",
        "## 2. Chi Tiết Kết Quả Truy Xuất Theo 5 Benchmark Queries",
        "",
    ])

    for bq in BENCHMARK_QUERIES:
        report_lines.extend([
            f"### Query: `{bq.id}` — {bq.category}",
            f"**Câu hỏi:** {bq.question}",
            f"**Gold Answer:** *{bq.gold_answer}*",
            f"**Kỳ vọng Doc ID:** `{bq.expected_doc_id}`",
        ])
        if bq.metadata_filter:
            report_lines.append(f"**Metadata Filter:** `{bq.metadata_filter}`")

        report_lines.append("")
        report_lines.append("| Strategy | Top-1 Score | Top-1 Doc ID | Top-1 Chunk Index | Top-1 Preview |")
        report_lines.append("|---|---|---|---|---|")

        for res in results:
            q_res = next(r for r in res["query_results"] if r["query_id"] == bq.id)
            top1 = q_res["retrieved_top_k"][0] if q_res["retrieved_top_k"] else {}
            score_str = f"{top1.get('score', 0.0):.4f}"
            doc_id_str = top1.get("doc_id", "N/A")
            chunk_idx_str = str(top1.get("chunk_index", "N/A"))
            prev_str = top1.get("preview", "").replace("|", "\\|")[:100]

            report_lines.append(
                f"| {res['strategy_name']} | {score_str} | `{doc_id_str}` | {chunk_idx_str} | {prev_str}... |"
            )
        report_lines.append("")

    report_lines.extend([
        "## 3. Nhận Xét Ưu Nhược Điểm Các Chiến Lược",
        "",
        "- **FixedSizeChunker (Cố định):** Đơn giản, độ dài đồng đều nhưng dễ làm gãy ngữ cảnh của câu và section.",
        "- **SentenceChunker (Theo câu):** Bảo toàn cấu trúc câu tốt, tuy nhiên kích thước chunk không ổn định do phụ thuộc độ dài đoạn văn.",
        "- **RecursiveChunker (Đệ quy):** Cân bằng xuất sắc giữa việc giữ toàn vẹn đoạn văn/câu và đảm bảo ranh giới kích thước tối đa.",
        "- **HeadingChunker (Domain-specific):** Giữ lại tiêu đề mục ngữ cảnh học vụ K3 trên từng chunk, tối ưu nhất cho bài toán tra cứu quy định đại học.",
    ])

    return "\n".join(report_lines)


def main() -> int:
    embedder = _select_embedder()
    logger.info(f"Using Embedding Backend: {getattr(embedder, '_backend_name', embedder.__class__.__name__)}")

    # Easy strategy toggle: Modify or add chunkers in this dictionary
    strategies_to_evaluate = [
        (
            "FixedSizeChunker",
            FixedSizeChunker(chunk_size=500, overlap=50),
            {"chunk_size": 500, "overlap": 50},
        ),
        (
            "SentenceChunker",
            SentenceChunker(max_sentences_per_chunk=3),
            {"max_sentences_per_chunk": 3},
        ),
        (
            "RecursiveChunker",
            RecursiveChunker(chunk_size=500),
            {"chunk_size": 500, "separators": r"['\n\n', '\n', '. ', ' ']"},
        ),
        (
            "HeadingChunker",
            HeadingChunker(chunk_size=500),
            {"chunk_size": 500, "heading_split": True},
        ),
    ]

    all_results = []
    for name, chunker, params in strategies_to_evaluate:
        res = run_benchmark_for_strategy(name, chunker, params, embedder)
        all_results.append(res)

    # Generate Markdown Report
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    report_content = generate_markdown_report(all_results)
    REPORT_FILE.write_text(report_content, encoding="utf-8")

    logger.info(f"\n" + "=" * 60)
    logger.info(f"BENCHMARK COMPLETED SUCCESSFULLY!")
    logger.info(f"Report saved to: {REPORT_FILE}")
    logger.info("=" * 60)

    print(report_content)
    return 0


if __name__ == "__main__":
    sys.exit(main())
