# Báo Cáo Cá Nhân — Lab 7: Embedding & Vector Store

**Họ tên:** Nguyễn Ngọc Dương
**Nhóm:** NEXACO
**Ngày:** 03/08/2026

> **Nộp 1 bản / sinh viên.** Phần nhóm (lựa chọn tài liệu, thiết kế chiến lược, bộ câu hỏi đánh giá, demo) nộp chung 1 bản trong `REPORT_NHOM.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần cá nhân: 60** = Khởi động (5) + Hướng tiếp cận (10) + Hoàn thiện code (30) + Dự đoán độ tương tự (5) + Kết quả truy xuất của tôi (10).

---

## 1. Khởi động (Warm-up) — Cá nhân (5 điểm)

### Độ tương tự Cosine (Cosine Similarity) (Bài tập 1.1)

**Độ tương tự cosine cao (High cosine similarity) nghĩa là gì?**
> Độ tương tự cosine cao (tiệm cận 1.0) thể hiện hai vector biểu diễn không gian có góc giữa chúng rất nhỏ, đồng nghĩa với việc hai đoạn văn bản có ý nghĩa ngữ nghĩa (semantic meaning) rất gần nhau, cho dù độ dài hay từ ngữ bề mặt có thể khác nhau.

**Ví dụ có độ tương tự CAO:**
- Câu A: "Sinh viên cần hoàn thành đăng ký thời khóa biểu trước thời hạn 20/06."
- Câu B: "Hạn cuối cùng để sinh viên xác nhận lịch học trên hệ thống là ngày 20/06."
- Tại sao tương đồng: Cả hai câu sử dụng các từ ngữ đồng nghĩa khác nhau ("hoàn thành đăng ký thời khóa biểu" vs "xác nhận lịch học", "thời hạn" vs "hạn cuối cùng") nhưng cùng diễn đạt một nội dung quy định học vụ.

**Ví dụ có độ tương tự THẤP:**
- Câu A: "Sinh viên đăng ký thời khóa biểu lớp học phần trên hệ thống QLĐT."
- Câu B: "Học viện cơ sở tại TP. Hồ Chí Minh đặt tại số 11 Nguyễn Đình Chiểu."
- Tại sao khác: Câu A nói về quy trình đăng ký môn học, trong khi câu B nói về địa chỉ địa lý của cơ sở đào tạo, không có sự liên quan về chủ đề.

**Tại sao độ tương tự cosine (cosine similarity) được ưu tiên hơn khoảng cách Euclid (Euclidean distance) cho text embeddings?**
> Độ tương tự cosine chỉ đo hướng của vector trong không gian mà không bị ảnh hưởng bởi độ dài (magnitude) của vector. Điều này giúp loại bỏ thiên vị do độ dài đoạn văn bản gây ra (đoạn văn dài chứa nhiều từ hơn thường có độ dài vector lớn hơn).

### Bài toán tính toán Chunking (Bài tập 1.2)

**Tài liệu 10,000 ký tự, chunk_size=500, overlap=50. Bao nhiêu chunks?**
> *Trình bày phép tính:*
> - Bước nhảy (step size) giữa các chunk: `step = chunk_size - overlap = 500 - 50 = 450` ký tự.
> - Số bước chuyển tiếp hoàn chỉnh: `(10,000 - 500) / 450 = 9,500 / 450 = 21.11`.
> - Số lượng chunks tạo ra là: `1 + ceil(21.11) = 1 + 22 = 23` chunks.
> *Đáp án:* **23 chunks**.

**Nếu độ chồng chéo (overlap) tăng lên 100, số lượng chunk thay đổi thế nào? Tại sao muốn độ chồng chéo nhiều hơn?**
> Khi overlap = 100, bước nhảy giảm xuống `400`, làm tăng tổng số chunk lên `1 + ceil(9,500 / 400) = 25` chunks (tăng 2 chunks). Chúng ta muốn độ chồng chéo nhiều hơn để giảm thiểu nguy cơ làm đứt gãy thông tin quan trọng nằm ngay ranh giới giữa hai chunk liên tiếp.

---

## 2. Hướng tiếp cận của tôi (My Approach) — Cá nhân (10 điểm)

### Các hàm chia nhỏ (Chunking Functions)

**`SentenceChunker.chunk`** — hướng tiếp cận:
> Tôi sử dụng biểu thức chính quy Lookbehind `r"(?<=[.!?])\s+"` để tách các câu mà vẫn bảo toàn dấu câu ở cuối. Xử lý các edge case như chuỗi rỗng, khoảng trắng thừa bằng `.strip()` và gom tối đa `max_sentences_per_chunk` câu vào mỗi chunk.

**`RecursiveChunker.chunk` / `_split`** — hướng tiếp cận:
> Thuật toán ưu tiên tách theo thứ tự danh sách phân cách `["\n\n", "\n", ". ", " ", ""]`. Base case là khi độ dài đoạn văn nhỏ hơn hoặc bằng `chunk_size` thì trả về ngay; nếu hết danh sách dấu phân cách mà đoạn vẫn lớn thì fallback về `FixedSizeChunker`.

### Lớp EmbeddingStore

**`add_documents` + `search`** — hướng tiếp cận:
> Dữ liệu được lưu trong mảng danh sách `_store` chứa các dictionary record chuẩn hóa (gồm `id`, `content`, `metadata`, `embedding`). Hàm `search` gọi helper `_search_records` để embed query đúng 1 lần, tính điểm tương đồng Cosine qua `compute_similarity` và xếp hạng giảm dần.

**`search_with_filter` + `delete_document`** — hướng tiếp cận:
> Trong `search_with_filter`, hệ thống thực hiện pre-filtering lọc các record có cặp `key: value` khớp 100% với `metadata_filter` trước, sau đó mới tính điểm tương đồng trên tập đã lọc. Hàm `delete_document` loại bỏ tất cả record có `metadata['doc_id'] == doc_id`.

### Tác tử KnowledgeBaseAgent

**`answer`** — hướng tiếp cận:
> Hàm `answer` gọi `store.search` để lấy top-k chunk liên quan nhất, sau đó ghép thành phần Context được đánh số `[1]`, `[2]`... đi kèm `doc_id`, `source`, `chunk_index` hỗ trợ trích dẫn nguồn gốc (grounding). Prompt yêu cầu LLM chỉ trả lời dựa vào Context và nói rõ nếu thiếu thông tin.

---

## 3. Hoàn thiện code (Core Implementation) — Cá nhân (30 điểm)

### Kết Quả Kiểm Thử (Test Results)

```text
============================= test session starts ==============================
platform linux -- Python 3.13.5, pytest-9.1.1, pluggy-1.6.0
rootdir: /home/admin123/Desktop/dataocubuntu/VinUni/K3-Day07-2A202601717-NguyenNgocDuong
collected 42 items

tests/test_solution.py::TestProjectStructure::test_root_main_entrypoint_exists PASSED [  2%]
tests/test_solution.py::TestProjectStructure::test_src_package_exists PASSED [  4%]
tests/test_solution.py::TestClassBasedInterfaces::test_chunker_classes_exist PASSED [  7%]
tests/test_solution.py::TestClassBasedInterfaces::test_mock_embedder_exists PASSED [  9%]
tests/test_solution.py::TestFixedSizeChunker::test_chunks_respect_size PASSED [ 11%]
tests/test_solution.py::TestFixedSizeChunker::test_correct_number_of_chunks_no_overlap PASSED [ 14%]
tests/test_solution.py::TestFixedSizeChunker::test_empty_text_returns_empty_list PASSED [ 16%]
tests/test_solution.py::TestFixedSizeChunker::test_no_overlap_no_shared_content PASSED [ 19%]
tests/test_solution.py::TestFixedSizeChunker::test_overlap_creates_shared_content PASSED [ 21%]
tests/test_solution.py::TestFixedSizeChunker::test_returns_list PASSED   [ 23%]
tests/test_solution.py::TestFixedSizeChunker::test_single_chunk_if_text_shorter PASSED [ 26%]
tests/test_solution.py::TestSentenceChunker::test_chunks_are_strings PASSED [ 28%]
tests/test_solution.py::TestSentenceChunker::test_respects_max_sentences PASSED [ 30%]
tests/test_solution.py::TestSentenceChunker::test_returns_list PASSED    [ 33%]
tests/test_solution.py::TestSentenceChunker::test_single_sentence_max_gives_many_chunks PASSED [ 35%]
tests/test_solution.py::TestRecursiveChunker::test_chunks_within_size_when_possible PASSED [ 38%]
tests/test_solution.py::TestRecursiveChunker::test_empty_separators_falls_back_gracefully PASSED [ 40%]
tests/test_solution.py::TestRecursiveChunker::test_handles_double_newline_separator PASSED [ 42%]
tests/test_solution.py::TestRecursiveChunker::test_returns_list PASSED   [ 45%]
tests/test_solution.py::TestEmbeddingStore::test_add_documents_increases_size PASSED [ 47%]
tests/test_solution.py::TestEmbeddingStore::test_add_more_increases_further PASSED [ 50%]
tests/test_solution.py::TestEmbeddingStore::test_initial_size_is_zero PASSED [ 52%]
tests/test_solution.py::TestEmbeddingStore::test_search_results_have_content_key PASSED [ 54%]
tests/test_solution.py::TestEmbeddingStore::test_search_results_have_score_key PASSED [ 57%]
tests/test_solution.py::TestEmbeddingStore::test_search_results_sorted_by_score_descending PASSED [ 59%]
tests/test_solution.py::TestEmbeddingStore::test_search_returns_at_most_top_k PASSED [ 61%]
tests/test_solution.py::TestEmbeddingStore::test_search_returns_list PASSED [ 64%]
tests/test_solution.py::TestKnowledgeBaseAgent::test_answer_non_empty PASSED [ 66%]
tests/test_solution.py::TestKnowledgeBaseAgent::test_answer_returns_string PASSED [ 69%]
tests/test_solution.py::TestComputeSimilarity::test_identical_vectors_return_1 PASSED [ 71%]
tests/test_solution.py::TestComputeSimilarity::test_opposite_vectors_return_minus_1 PASSED [ 73%]
tests/test_solution.py::TestComputeSimilarity::test_orthogonal_vectors_return_0 PASSED [ 76%]
tests/test_solution.py::TestComputeSimilarity::test_zero_vector_returns_0 PASSED [ 78%]
tests/test_solution.py::TestCompareChunkingStrategies::test_counts_are_positive PASSED [ 80%]
tests/test_solution.py::TestCompareChunkingStrategies::test_each_strategy_has_count_and_avg_length PASSED [ 83%]
tests/test_solution.py::TestCompareChunkingStrategies::test_returns_three_strategies PASSED [ 85%]
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_filter_by_department PASSED [ 88%]
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_no_filter_returns_all_candidates PASSED [ 90%]
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_returns_at_most_top_k PASSED [ 92%]
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_reduces_collection_size PASSED [ 95%]
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_returns_false_for_nonexistent_doc PASSED [ 97%]
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_returns_true_for_existing_doc PASSED [100%]

============================== 42 passed in 0.10s ==============================
```

**Số lượng bài test vượt qua (pass):** **42 / 42**

---

## 4. Dự đoán độ tương tự (Similarity Predictions) — Cá nhân (5 điểm)

| Cặp | Câu A | Câu B | Dự đoán | Điểm thực tế | Đúng? |
|------|-----------|-----------|---------|--------------|-------|
| 1 | Học viện Công nghệ Bưu chính Viễn thông thông báo hủy lớp học phần. | Phòng Giáo vụ thông báo hủy 16 lớp học phần do không đủ sĩ số. | cao | 0.6825 | Đúng |
| 2 | Sinh viên đăng ký lịch học theo tiến trình rút gọn học kỳ 1. | Quy trình đăng ký nguyện vọng học vượt trên cổng quản lý đào tạo. | cao | 0.5368 | Đúng |
| 3 | Lịch nghỉ Tết Dương lịch năm 2026 của sinh viên. | Danh sách sinh viên bị hủy môn học Tiếng Anh CLC. | thấp | 0.1433 | Đúng |
| 4 | Học phí học kỳ phụ và chế độ chính sách học bổng. | Địa chỉ trụ sở chính Học viện tại 122 Hoàng Quốc Việt Hà Nội. | thấp | 0.1354 | Đúng |
| 5 | Đăng ký thời khóa biểu các lớp học phần trong kỳ hè. | Mô hình học máy và cơ sở dữ liệu vector store. | thấp | 0.2017 | Đúng |

**Kết quả nào bất ngờ nhất? Điều này nói gì về cách embeddings biểu diễn ý nghĩa?**
> Cặp 5 có chủ đề hoàn toàn khác nhau (đăng ký môn học vs machine learning) nhưng vẫn đạt điểm 0.2017 do có xuất hiện các từ chung như "hệ thống", "cơ sở". Điều này chứng minh embeddings biểu diễn ý nghĩa trong không gian liên tục nhiều chiều (dense space), nơi các từ vựng dùng trong bối cảnh kỹ thuật/hành chính vẫn giữ một lượng tương đồng nhỏ.

---

## 5. Kết quả truy xuất của tôi (Competition Results) — Cá nhân (10 điểm)

Chạy **5 câu hỏi đánh giá của nhóm** trên mã nguồn cá nhân của bạn trong gói `src`. **5 câu hỏi này phải trùng với các thành viên cùng nhóm** (xem `REPORT_NHOM.md`).

| # | Câu hỏi (Query) | Top-1 Chunk truy xuất được (tóm tắt) | Điểm Score | Có liên quan không? (Relevant) | Câu trả lời của Agent (tóm tắt) |
|---|-------|--------------------------------|-------|-----------|------------------------|
| 1 | Số lượng lớp học phần bị hủy do không đủ điều kiện mở lớp kỳ phụ 2025-2026? | Hủy 16 lớp học phần do số lượng sinh viên đăng ký thời khóa biểu không đủ... | 0.6850 | Có | Phòng Giáo vụ thông báo hủy 16 lớp học phần do sĩ số không đủ điều kiện mở lớp. |
| 2 | Điều kiện để sinh viên khóa 2024, 2025 đăng ký học theo tiến trình rút gọn? | Sinh viên phải đăng ký đầy đủ môn theo tiến trình, không đăng ký ngoài tiến trình... | 0.5420 | Có | Sinh viên phải chọn đầy đủ môn học vượt, không đăng ký học cải thiện/học lại. |
| 3 | Quy trình các bước đăng ký nguyện vọng học vượt trên QLĐT? | Bước 1: Đăng nhập Hệ thống QLĐT chọn Đăng ký nguyện vọng. Bước 2: Nhập mã học phần. Bước 3: Nhấn nút Đăng ký... | 0.6120 | Có | Quy trình gồm 3 bước: Đăng nhập chọn Đăng ký nguyện vọng, nhập mã môn và bấm Đăng ký. |
| 4 | Liệt kê danh sách môn học bị hủy đợt học lại kỳ phụ (hè) 2025-2026? | Danh sách 16 môn bị hủy: Tiếng Anh CLC, Thị giác máy tính, Toán rời rạc 2... | 0.4890 | Có | Danh sách môn bị hủy bao gồm 16 môn như Tiếng Anh CLC, Thị giác máy tính, Java... |
| 5 | Thông tin dành riêng cho sinh viên (audience=student) về xử lý môn học bị hủy? | Phòng Giáo vụ sẽ tự động hủy kết quả đăng ký của SV trên hệ thống, SV không cần làm Đơn... | 0.5980 | Có | Giáo vụ sẽ tự động hủy kết quả đăng ký trên hệ thống, SV không cần làm đơn đề nghị. |

**Bao nhiêu câu hỏi trả về chunk có liên quan trong top-3?** **5 / 5**

**Điều hay nhất tôi học được từ thành viên khác / nhóm khác (qua demo):**
> Tôi học được kỹ thuật `HeadingChunker` kết hợp bảo tồn tiêu đề mục (`#`, `##`) khi chia nhỏ tài liệu quy định đại học. Việc bổ sung ngữ cảnh tiêu đề giúp tăng độ tương đồng ngữ nghĩa đáng kể và giảm hiện tượng trích xuất nhầm đoạn khi câu hỏi quá ngắn.

---

## Tự Đánh Giá (Phần Cá Nhân)

| Tiêu chí | Điểm tự đánh giá |
|----------|-------------------|
| Khởi động (Warm-up) | 5 / 5 |
| Hướng tiếp cận của tôi (My Approach) | 10 / 10 |
| Hoàn thiện code (Core Implementation — tests) | 30 / 30 |
| Dự đoán độ tương tự (Similarity Predictions) | 5 / 5 |
| Kết quả truy xuất của tôi (Competition Results) | 10 / 10 |
| **Tổng phần cá nhân** | **60 / 60** |
