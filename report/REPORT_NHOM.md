# Báo Cáo Nhóm — Lab 7: Embedding & Vector Store

**Nhóm:** NEXACO
**Thành viên:**
| Họ và tên | Mã học viên |
|----------------|------|
| Nguyễn Ngọc Dương | 2A202601717 |
| Lê Văn Long | 2A202601711 |
**Ngày:** 03/08/2026

> **Nộp 1 bản / nhóm.** Phần cá nhân (hướng tiếp cận, kết quả riêng, dự đoán…) mỗi thành viên nộp riêng trong `REPORT_CANHAN.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần nhóm: 40** = Lựa chọn tài liệu (10) + Thiết kế chiến lược (15) + Chất lượng truy xuất (10) + Thuyết trình (5).

---

## 1. Lựa chọn tài liệu (Document Set Quality) — Nhóm (10 điểm)

### Phạm vi bộ tài liệu (Scope)

**Chủ đề (cố định theo lớp K3):** Dịch vụ / quy định đại học (đăng ký môn, học phí, học bổng, thư viện, ký túc xá…).

**Phạm vi cụ thể nhóm tập trung:**
> Nhóm tập trung thu thập toàn bộ các thông báo, quy định và kế hoạch đăng ký học phần, thời khóa biểu, học phụ/kỳ hè, học vượt và các xử lý học vụ chính thức từ Phòng Giáo vụ — Học viện Công nghệ Bưu chính Viễn thông (PTIT).

### Danh sách tài liệu (Data Inventory)

| # | Tên tài liệu | Nguồn (Source URL) | Ngày lấy / Phiên bản | Số ký tự | Metadata đã gán |
|---|--------------|------------|--------------------|----------|-----------------|
| 1 | Đăng ký học phần - PTIT | https://giaovu.ptit.edu.vn/ke-hoach-dao-tao/dang-ky-hoc-phan/ | 2026-08-03 / 2026.1 | 1,122 | `doc_id`, `title`, `audience`, `department`, `language`, `source_url`, `document_version` |
| 2 | Thông báo hủy các lớp học phần đợt học lại kỳ phụ (hè) 2025-2026 | https://giaovu.ptit.edu.vn/thong-bao-v-v-huy-cac-lop-hoc-phan-dot-hoc-lai-ky-phu-he-nam-hoc-2025-2026/ | 2026-08-03 / 15/06/2026 | 2,734 | `doc_id`, `title`, `audience`, `department`, `language`, `source_url`, `document_version` |
| 3 | Đăng ký lịch học cho sinh viên khóa 2024, 2025 học tiến trình rút gọn kỳ 1 | https://giaovu.ptit.edu.vn/dang-ky-lich-hoc-thoi-khoa-bieu-cho-sinh-vien-khoa-2024-2025-hoc-theo-tien-trinh-rut-gon-cua-hoc-ky-i-nam-hoc-2026-2027/ | 2026-08-03 / 16/06/2026 | 5,181 | `doc_id`, `title`, `audience`, `department`, `language`, `source_url`, `document_version` |
| 4 | Tổ chức đăng ký học vượt học kỳ I năm học 2026-2027 cho khóa 2024, 2025 | https://giaovu.ptit.edu.vn/to-chuc-dang-ky-hoc-vuot-hoc-ky-i-nam-hoc-2026-2027-doi-voi-sinh-vien-khoa-2024-2025/ | 2026-08-03 / 02/06/2026 | 3,235 | `doc_id`, `title`, `audience`, `department`, `language`, `source_url`, `document_version` |
| 5 | Điều chỉnh lịch đăng ký học lại, học cải thiện trên QLĐT kỳ 2 | https://giaovu.ptit.edu.vn/dieu-chinh-lich-dang-ky-hoc-lai-hoc-cai-thien-hoc-2-van-bang-tren-qldt-hoc-ky-2-nam-hoc-2025-2026/ | 2026-08-03 / 08/01/2026 | 2,259 | `doc_id`, `title`, `audience`, `department`, `language`, `source_url`, `document_version` |

**Danh sách kiểm tra quản trị dữ liệu (Data governance checklist):**
- [x] Tập tài liệu (Corpus) chỉ chứa nguồn công khai/được phép dùng và không chứa dữ liệu cá nhân, thông tin đăng nhập hoặc tài liệu nội bộ.
- [x] Mỗi tài liệu có `source_url`, `retrieved_at`, `document_version` (hoặc ngày hiệu lực) trong metadata.

### Cấu trúc Metadata (Metadata Schema)

| Trường metadata | Kiểu | Ví dụ giá trị | Tại sao hữu ích cho truy xuất (retrieval)? |
|----------------|------|---------------|-------------------------------|
| `doc_id` | `str` | `k3-course-registration` | Định danh duy nhất tài liệu, hỗ trợ xóa toàn bộ chunk hoặc nhóm nhóm truy xuất. |
| `audience` | `str` | `student` | Phân loại đối tượng áp dụng (`student`, `faculty`, `staff`), ngăn việc trả về nhầm văn bản nội bộ cho sinh viên khi lọc metadata. |
| `department` | `str` | `academic-affairs` | Xác định đơn vị quản lý quy định (Phòng Giáo vụ, Phòng CTSV,...), tối ưu hóa pre-filtering. |
| `document_version` | `str` | `15/06/2026` | Đảm bảo tính mới của thông tin, phục vụ truy vấn các mốc thời gian cập nhật. |

---

## 2. Thiết kế chiến lược (Strategy Design) — Nhóm (15 điểm)

### Phân tích đường cơ sở (Baseline Analysis)

Chạy `ChunkingStrategyComparator().compare()` trên các tài liệu đã làm sạch:

| Tài liệu | Chiến lược (Strategy) | Số lượng Chunk | Độ dài trung bình | Giữ được ngữ cảnh không? |
|-----------|----------|-------------|------------|-------------------|
| `dang-ky-lich-hoc-...md` | FixedSizeChunker (`fixed_size`) | 8 | 484.6 chars | Trung bình (cắt ngẫu nhiên giữa các đoạn). |
| `dang-ky-lich-hoc-...md` | SentenceChunker (`by_sentences`) | 5 | 620.1 chars | Khá (giữ đúng ranh giới câu). |
| `dang-ky-lich-hoc-...md` | RecursiveChunker (`recursive`) | 9 | 390.2 chars | Tốt (bảo tồn phân đoạn `\n\n` và `\n`). |
| `dang-ky-lich-hoc-...md` | HeadingChunker (`heading`) | 9 | 450.5 chars | Rất tốt (giữ tiêu đề `#` mục trong ngữ cảnh). |

### Chiến lược của từng thành viên

**Thành viên 1 — Nguyễn Ngọc Dương**
- **Loại chiến lược:** Custom Domain Chunker (`HeadingChunker` kế thừa `RecursiveChunker`)
- **Mô tả & lý do chọn cho chủ đề này:** Dữ liệu quy chế/thông báo PTIT chứa các mục tiêu đề phân cấp (`#`, `##`). `HeadingChunker` tự động gom nhóm văn bản theo tiêu đề trước, sau đó dùng `RecursiveChunker` cắt mịn và đính kèm lại tiêu đề mục ở đầu mỗi chunk con, giúp bảo toàn ý nghĩa ngữ nghĩa khi tìm kiếm vector.
- **Code snippet (nếu custom):**
```python
class HeadingChunker:
    def __init__(self, chunk_size: int = 500) -> None:
        self.chunk_size = chunk_size
        self.recursive_chunker = RecursiveChunker(chunk_size=chunk_size)

    def chunk(self, text: str) -> list[str]:
        heading_pattern = r"(?=\n#{1,4}\s+)"
        sections = [s.strip() for s in re.split(heading_pattern, text) if s.strip()]
        final_chunks = []
        for sec in sections:
            if len(sec) <= self.chunk_size:
                final_chunks.append(sec)
            else:
                lines = sec.splitlines()
                heading_prefix = lines[0] if lines[0].startswith("#") else ""
                sub_chunks = self.recursive_chunker.chunk(sec)
                for sc in sub_chunks:
                    if heading_prefix and not sc.startswith("#"):
                        sc = f"{heading_prefix}\n{sc}"
                    final_chunks.append(sc)
        return final_chunks
```

**Thành viên 2 — Lê Văn Long**
- **Loại chiến lược:** `RecursiveChunker` (`chunk_size=500`, `separators=["\n\n", "\n", ". ", " "]`)
- **Mô tả & lý do chọn:** Cắt văn bản theo các cấp độ tự nhiên của văn bản hành chính: xuống dòng kép (đoạn), xuống dòng đơn (dòng liệt kê), sau đó mới tới dấu câu.
- **Code snippet (nếu custom):** `RecursiveChunker(chunk_size=500)`

### So Sánh Giữa Các Thành Viên

| Thành viên | Chiến lược (Strategy) | Điểm truy xuất (/10) | Điểm mạnh | Điểm yếu |
|-----------|----------|----------------------|-----------|----------|
| Nguyễn Ngọc Dương | `HeadingChunker` | 10 / 10 | Bảo toàn ngữ cảnh tiêu đề mục, điểm retrieval precision cao nhất (80%). | Phụ thuộc vào định dạng Markdown chuẩn tiêu đề. |
| Lê Văn Long | `RecursiveChunker` | 8 / 10 | Linh hoạt, cắt mượt theo dòng trống và ranh giới đoạn. | Dễ làm mất tiêu đề mục nếu đoạn cắt nằm xa tiêu đề. |

**Chiến lược nào tốt nhất cho chủ đề này? Tại sao?**
> Chiến lược **`HeadingChunker`** (kết hợp `RecursiveChunker`) là tốt nhất cho chủ đề quy định/dịch vụ đại học. Lý do là văn bản học vụ có cấu trúc chia thành các mục/khoản rõ ràng; việc giữ lại tiêu đề mục ở đầu mỗi chunk con giúp mô hình embedding (như `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`) định vị chính xác bối cảnh ngữ nghĩa khi thực hiện cosine similarity.

---

## 3. Câu hỏi đánh giá & Chất lượng truy xuất (Retrieval Quality) — Nhóm (10 điểm)

### Câu hỏi đánh giá & Câu trả lời chuẩn (nhóm thống nhất)

| # | Câu hỏi (Query) | Câu trả lời chuẩn (Gold Answer) | Chunk nào chứa thông tin? |
|---|-------|-------------------------------|--------------------------|
| 1 | Số lượng lớp học phần bị hủy do số lượng sinh viên đăng ký thời khóa biểu không đủ điều kiện mở lớp trong đợt học lại kỳ phụ năm 2025-2026 là bao nhiêu? | Hủy 16 lớp học phần do số lượng sinh viên đăng ký thời khóa biểu không đủ điều kiện mở lớp. | `thong-bao-v-v-huy-cac-lop-hoc-phan-dot-hoc-lai-ky-phu-he-nam-hoc-2025-2026::chunk_0` |
| 2 | Điều kiện để sinh viên đại học chính quy khóa 2024, 2025 được đăng ký lịch học theo tiến trình rút gọn học kỳ I năm học 2026-2027 là gì? | Sinh viên phải đăng ký đầy đủ môn theo tiến trình rút gọn, không đăng ký môn ngoài tiến trình và không đăng ký học lại/cải thiện. | `dang-ky-lich-hoc-thoi-khoa-bieu-cho-sinh-vien-khoa-2024-2025...::chunk_1` |
| 3 | Quy trình các bước sinh viên thực hiện đăng ký nguyện vọng học vượt học kỳ I năm học 2026-2027 trên hệ thống QLĐT? | Bước 1: Đăng nhập Hệ thống QLĐT chọn 'Đăng ký nguyện vọng'. Bước 2: Nhập mã học phần. Bước 3: Nhấn nút 'Đăng ký'. | `to-chuc-dang-ky-hoc-vuot-hoc-ky-i-nam-hoc-2026-2027...::chunk_1` |
| 4 | Liệt kê danh sách các môn học bị hủy trong đợt học lại kỳ phụ (hè) năm học 2025-2026? | 16 môn bị hủy bao gồm Tiếng Anh CLC, Thị giác máy tính, Cơ sở đo lường điện tử, Truyền thông số, Marketing căn bản, Java,... | `thong-bao-v-v-huy-cac-lop-hoc-phan-dot-hoc-lai-ky-phu-he-nam-hoc-2025-2026::chunk_1` |
| 5 | Thông tin dành riêng cho sinh viên (audience=student) về xử lý đối với sinh viên có học phần bị hủy do không đủ sĩ số? | Phòng Giáo vụ sẽ tự động hủy kết quả đăng ký của SV trên hệ thống, SV không cần thao tác hủy hay làm Đơn đề nghị. | `thong-bao-v-v-huy-cac-lop-hoc-phan-dot-hoc-lai-ky-phu-he-nam-hoc-2025-2026::chunk_2` |

### Tổng hợp chất lượng truy xuất của nhóm

| # | Câu hỏi | Chiến lược tốt nhất cho câu này | Có chunk liên quan trong top-3? | Ghi chú |
|---|---------|-------------------------------|-------------------------------|---------|
| 1 | Số lượng lớp học phần bị hủy? | `FixedSizeChunker` / `RecursiveChunker` | Có (Top-1) | Trả về chính xác thông báo hủy 16 lớp học phần. |
| 2 | Điều kiện đăng ký tiến trình rút gọn? | `HeadingChunker` | Có (Top-1) | Giữ được mục "Nguyên tắc đăng ký" kèm tiêu đề. |
| 3 | Quy trình các bước đăng ký học vượt? | `HeadingChunker` / `FixedSizeChunker` | Có (Top-1) | Trả về trọn vẹn 3 bước hướng dẫn. |
| 4 | Liệt kê các môn học bị hủy đợt hè? | `SentenceChunker` / `HeadingChunker` | Có (Top-2) | Truy xuất được bảng danh sách 16 môn học. |
| 5 | Xử lý học phần bị hủy (audience=student)? | `HeadingChunker` (+ Metadata Filter) | Có (Top-1) | Nhờ lọc `audience=student` nên loại bỏ toàn bộ thông báo khác. |

**Lọc bằng metadata có giúp ích không? Ở câu hỏi nào?**
> Lọc metadata tỏ ra đặc biệt hiệu quả ở **Câu hỏi số 5** (`Q5_FILTER_EXCEPTION`). Việc áp dụng pre-filter `metadata_filter={"audience": "student", "department": "academic-affairs"}` giúp loại bỏ 100% các văn bản không dành cho sinh viên trước khi tính điểm cosine similarity, nâng chính xác vị trí Top-1 lên tuyệt đối.

---

## 4. Thuyết trình (Demo) & Bài học nhóm — Nhóm (5 điểm)

**Những phân tích (insights) hay nhất nhóm sẽ trình bày:**
> 1. **Kiến trúc Chunking phân cấp (Heading + Recursive):** Là chìa khóa giải quyết bài toán tra cứu văn bản quy chế đại học có cấu trúc phân mục.
> 2. **Tác động thực tế của Metadata Pre-Filtering:** Giúp loại bỏ nhiễu ngữ nghĩa (semantic noise) từ các đơn vị quản lý khác trước khi chạy embedding retrieval.
> 3. **Tầm quan trọng của Caching Embedding:** Giúp tăng tốc độ benchmark lên gấp 5-10 lần mà vẫn đảm bảo tính công bằng và nhất quán giữa các chiến lược.

**Bài học rút ra khi so sánh trong nhóm:**
> Cùng một bộ tài liệu nguồn nhưng nếu chỉ dùng `FixedSizeChunker` cắt ngẫu nhiên sẽ dễ làm "gãy" ranh giới thông tin (ví dụ: chia cắt các bước trong một quy trình). Việc áp dụng `HeadingChunker` giúp giữ nguyên bối cảnh tiêu đề mục ở đầu mỗi đoạn cắt.

**Nếu làm lại, nhóm sẽ thay đổi gì trong chiến lược dữ liệu (data strategy)?**
> Nhóm sẽ thiết kế thêm cơ chế **Parent-Child Chunking** (hoặc Auto-Merging Retriever): sử dụng chunk nhỏ (child) để matching vector đạt độ tương đồng cao, nhưng khi gửi cho LLM sẽ trả về toàn bộ đoạn lớn (parent) để sinh câu trả lời đầy đủ ngữ cảnh nhất.

---

## Tự Đánh Giá (Phần Nhóm)

| Tiêu chí | Điểm tự đánh giá |
|----------|-------------------|
| Lựa chọn tài liệu (Document Set Quality) | 10 / 10 |
| Thiết kế chiến lược (Strategy Design) | 15 / 15 |
| Chất lượng truy xuất (Retrieval Quality) | 10 / 10 |
| Thuyết trình (Demo) | 5 / 5 |
| **Tổng phần nhóm** | **40 / 40** |
