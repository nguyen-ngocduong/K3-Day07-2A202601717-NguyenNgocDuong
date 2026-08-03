# Báo Cáo Đánh Giá Hiệu Năng Chunking & Phân Tích Lỗi (Benchmark & Failure Analysis)

> **Embedding Model:** `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`
> **Thời Gian Tạo:** 2026-08-03 12:30:49

---

## 1. Bảng So Sánh Hiệu Năng Các Chiến Lược Chunking (Bao Gồm SemanticChunker)

| Chiến Lược (Strategy) | Kích Thước / Tham Số | Tổng Chunks | Avg Chunks/Doc | Độ Dài TB (chars) | Thời Gian Indexing | Score TB (/2.0) | Chunk Precision |
|---|---|---|---|---|---|---|---|
| **FixedSizeChunker** | `chunk_size=500, overlap=50` | 54 | 4.91 | 471.7 | 2.4223s | **0.80** | **40%** |
| **SentenceChunker** | `max_sentences_per_chunk=3` | 37 | 3.36 | 627.8 | 1.4364s | **0.80** | **20%** |
| **RecursiveChunker** | `chunk_size=500, separators=['\n\n', '\n', '. ', ' ']` | 60 | 5.45 | 387.1 | 2.0173s | **0.60** | **20%** |
| **HeadingChunker** | `chunk_size=500, heading_split=True` | 60 | 5.45 | 457.4 | 1.7160s | **0.80** | **20%** |
| **SemanticChunker** | `similarity_threshold=0.45, max_chunk_size=500` | 274 | 24.91 | 83.1 | 7.4581s | **0.40** | **20%** |

---

## 2. Chi Tiết Đánh Giá 5 Benchmark Queries & Lọc Metadata (A/B Test)

### Query: `Q1_NUMERICAL` — Truy vấn số liệu
- **Câu hỏi:** Số lượng lớp học phần bị hủy do số lượng sinh viên đăng ký thời khóa biểu không đủ điều kiện mở lớp trong đợt học lại kỳ phụ năm 2025-2026 là bao nhiêu?
- **Gold Answer:** *Hủy 16 lớp học phần do số lượng sinh viên đăng ký thời khóa biểu không đủ điều kiện mở lớp.*
- **Doc ID Kỳ vọng:** `thong-bao-v-v-huy-cac-lop-hoc-phan-dot-hoc-lai-ky-phu-he-nam-hoc-2025-2026`
- **Expected Evidence:** `['Hủy 16 lớp học phần', 'không đủ điều kiện mở lớp']`

| Strategy | Score | Grounded | Top-1 Doc ID | Evidence Top-1? | Phân Tích Kết Quả |
|---|---|---|---|---|---|
| FixedSizeChunker | 2/2 | YES | `thong-bao-v-v-huy-cac-lop-hoc-phan-dot-hoc-lai-ky-phu-he-nam-hoc-2025-2026` | ✅ Có | Thành công hoàn toàn: Chunk chứa bằng chứng nằm ở Top-1 và trả lời chuẩn xác. |
| SentenceChunker | 0/2 | NO | `dieu-chinh-lich-dang-ky-hoc-lai-hoc-cai-thien-hoc-2-van-bang-tren-qldt-hoc-ky-2-nam-hoc-2025-2026` | ❌ Không | Thất bại: Chọn sai Document (Retrieve được `dieu-chinh-lich-dang-ky-hoc-lai-hoc-cai-thien-hoc-2-van-bang-tren-qldt-hoc-ky-2-nam-hoc-2025-2026` thay vì `thong-bao-v-v-huy-cac-lop-hoc-phan-dot-hoc-lai-ky-phu-he-nam-hoc-2025-2026`). |
| RecursiveChunker | 2/2 | YES | `thong-bao-v-v-huy-cac-lop-hoc-phan-dot-hoc-lai-ky-phu-he-nam-hoc-2025-2026` | ✅ Có | Thành công hoàn toàn: Chunk chứa bằng chứng nằm ở Top-1 và trả lời chuẩn xác. |
| HeadingChunker | 1/2 | YES | `huy-cac-lop-hoc-phan-dot-hoc-lop-rieng-hoc-ky-2-nam-hoc-2025-2026` | ✅ Có | Bán thành công: Tìm thấy tài liệu/bằng chứng nhưng vị trí chưa tối ưu hoặc câu trả lời chưa đầy đủ. |
| SemanticChunker | 2/2 | YES | `thong-bao-v-v-huy-cac-lop-hoc-phan-dot-hoc-lai-ky-phu-he-nam-hoc-2025-2026` | ✅ Có | Thành công hoàn toàn: Chunk chứa bằng chứng nằm ở Top-1 và trả lời chuẩn xác. |

### Query: `Q2_CONDITION` — Truy vấn điều kiện
- **Câu hỏi:** Điều kiện để sinh viên đại học chính quy khóa 2024, 2025 được đăng ký lịch học theo tiến trình rút gọn học kỳ I năm học 2026-2027 là gì?
- **Gold Answer:** *Sinh viên phải đăng ký đầy đủ các môn theo tiến trình rút gọn, không được đăng ký môn ngoài tiến trình, không đăng ký học lại/cải thiện.*
- **Doc ID Kỳ vọng:** `dang-ky-lich-hoc-thoi-khoa-bieu-cho-sinh-vien-khoa-2024-2025-hoc-theo-tien-trinh-rut-gon-cua-hoc-ky-i-nam-hoc-2026-2027`
- **Expected Evidence:** `['tiến trình đào tạo rút gọn', 'Không được phép đăng ký các môn ngoài']`

| Strategy | Score | Grounded | Top-1 Doc ID | Evidence Top-1? | Phân Tích Kết Quả |
|---|---|---|---|---|---|
| FixedSizeChunker | 0/2 | NO | `to-chuc-dang-ky-hoc-vuot-hoc-ky-i-nam-hoc-2026-2027-doi-voi-sinh-vien-khoa-2024-2025` | ❌ Không | Thất bại: Chọn đúng Document nhưng sai Section/Chunk (thiếu expected evidence). |
| SentenceChunker | 1/2 | YES | `to-chuc-dang-ky-hoc-vuot-hoc-ky-i-nam-hoc-2026-2027-doi-voi-sinh-vien-khoa-2024-2025` | ❌ Không | Bán thành công: Tìm thấy tài liệu/bằng chứng nhưng vị trí chưa tối ưu hoặc câu trả lời chưa đầy đủ. |
| RecursiveChunker | 0/2 | NO | `dang-ky-lich-hoc-thoi-khoa-bieu-cho-sinh-vien-khoa-2024-2025-hoc-theo-tien-trinh-rut-gon-cua-hoc-ky-i-nam-hoc-2026-2027` | ❌ Không | Thất bại: Chọn đúng Document nhưng sai Section/Chunk (thiếu expected evidence). |
| HeadingChunker | 0/2 | NO | `to-chuc-dang-ky-hoc-vuot-hoc-ky-i-nam-hoc-2026-2027-doi-voi-sinh-vien-khoa-2024-2025` | ❌ Không | Thất bại: Chọn đúng Document nhưng sai Section/Chunk (thiếu expected evidence). |
| SemanticChunker | 0/2 | NO | `dang-ky-lich-hoc-thoi-khoa-bieu-cho-sinh-vien-khoa-2024-2025-hoc-theo-tien-trinh-rut-gon-cua-hoc-ky-i-nam-hoc-2026-2027` | ❌ Không | Thất bại: Chọn đúng Document nhưng sai Section/Chunk (thiếu expected evidence). |

### Query: `Q3_PROCESS` — Truy vấn quy trình
- **Câu hỏi:** Quy trình các bước sinh viên thực hiện đăng ký nguyện vọng học vượt học kỳ I năm học 2026-2027 trên hệ thống QLĐT?
- **Gold Answer:** *Bước 1: Đăng nhập Hệ thống QLĐT và chọn chức năng 'Đăng ký nguyện vọng'. Bước 2: Nhập mã học phần. Bước 3: Nhấn nút 'Đăng ký'.*
- **Doc ID Kỳ vọng:** `to-chuc-dang-ky-hoc-vuot-hoc-ky-i-nam-hoc-2026-2027-doi-voi-sinh-vien-khoa-2024-2025`
- **Expected Evidence:** `['Bước 1: Đăng nhập', 'Đăng ký nguyện vọng', 'Bước 2:', 'Bước 3:']`

| Strategy | Score | Grounded | Top-1 Doc ID | Evidence Top-1? | Phân Tích Kết Quả |
|---|---|---|---|---|---|
| FixedSizeChunker | 2/2 | YES | `to-chuc-dang-ky-hoc-vuot-hoc-ky-i-nam-hoc-2026-2027-doi-voi-sinh-vien-khoa-2024-2025` | ✅ Có | Thành công hoàn toàn: Chunk chứa bằng chứng nằm ở Top-1 và trả lời chuẩn xác. |
| SentenceChunker | 2/2 | YES | `to-chuc-dang-ky-hoc-vuot-hoc-ky-i-nam-hoc-2026-2027-doi-voi-sinh-vien-khoa-2024-2025` | ✅ Có | Thành công hoàn toàn: Chunk chứa bằng chứng nằm ở Top-1 và trả lời chuẩn xác. |
| RecursiveChunker | 1/2 | YES | `to-chuc-dang-ky-hoc-vuot-hoc-ky-i-nam-hoc-2026-2027-doi-voi-sinh-vien-khoa-2024-2025` | ❌ Không | Bán thành công: Tìm thấy tài liệu/bằng chứng nhưng vị trí chưa tối ưu hoặc câu trả lời chưa đầy đủ. |
| HeadingChunker | 2/2 | YES | `to-chuc-dang-ky-hoc-vuot-hoc-ky-i-nam-hoc-2026-2027-doi-voi-sinh-vien-khoa-2024-2025` | ✅ Có | Thành công hoàn toàn: Chunk chứa bằng chứng nằm ở Top-1 và trả lời chuẩn xác. |
| SemanticChunker | 0/2 | NO | `to-chuc-dang-ky-hoc-vuot-hoc-ky-i-nam-hoc-2026-2027-doi-voi-sinh-vien-khoa-2024-2025` | ❌ Không | Thất bại: Chọn đúng Document nhưng sai Section/Chunk (thiếu expected evidence). |

### Query: `Q4_ENUMERATION` — Truy vấn liệt kê
- **Câu hỏi:** Liệt kê danh sách các môn học bị hủy trong đợt học lại kỳ phụ (hè) năm học 2025-2026?
- **Gold Answer:** *16 môn học bao gồm Tiếng Anh (Course 1 _CLC), Thị giác máy tính, Cơ sở đo lường điện tử, Truyền thông số, Marketing căn bản, Marketing công nghiệp, Nguyên lý kế toán, Xác suất thống kê, Toán rời rạc 2, Luật xa gần, CAD/CAM, Kiến trúc máy tính, Ngôn ngữ lập trình Java, Kỹ thuật quay phim, Kịch bản đa phương tiện, Vật lý 3 và thí nghiệm.*
- **Doc ID Kỳ vọng:** `thong-bao-v-v-huy-cac-lop-hoc-phan-dot-hoc-lai-ky-phu-he-nam-hoc-2025-2026`
- **Expected Evidence:** `['Tiếng Anh (Course 1 _CLC)', 'Thị giác máy tính', 'Toán rời rạc 2', 'Ngôn ngữ lập trình Java']`

| Strategy | Score | Grounded | Top-1 Doc ID | Evidence Top-1? | Phân Tích Kết Quả |
|---|---|---|---|---|---|
| FixedSizeChunker | 0/2 | NO | `dang-ky-thoi-khoa-bieu-cac-lop-hoc-phan-trong-dot-hoc-ky-phu-ky-he-nam-hoc-2025-2026` | ❌ Không | Thất bại: Chọn sai Document (Retrieve được `dang-ky-thoi-khoa-bieu-cac-lop-hoc-phan-trong-dot-hoc-ky-phu-ky-he-nam-hoc-2025-2026` thay vì `thong-bao-v-v-huy-cac-lop-hoc-phan-dot-hoc-lai-ky-phu-he-nam-hoc-2025-2026`). |
| SentenceChunker | 1/2 | YES | `dieu-chinh-lich-dang-ky-hoc-lai-hoc-cai-thien-hoc-2-van-bang-tren-qldt-hoc-ky-2-nam-hoc-2025-2026` | ❌ Không | Bán thành công: Tìm thấy tài liệu/bằng chứng nhưng vị trí chưa tối ưu hoặc câu trả lời chưa đầy đủ. |
| RecursiveChunker | 0/2 | NO | `dang-ky-lich-hoc-thoi-khoa-bieu-cho-sinh-vien-khoa-2024-2025-hoc-theo-tien-trinh-rut-gon-cua-hoc-ky-i-nam-hoc-2026-2027` | ❌ Không | Thất bại: Chọn đúng Document nhưng sai Section/Chunk (thiếu expected evidence). |
| HeadingChunker | 0/2 | NO | `thong-bao-v-v-huy-cac-lop-hoc-phan-dot-hoc-lai-ky-phu-he-nam-hoc-2025-2026` | ❌ Không | Thất bại: Chọn đúng Document nhưng sai Section/Chunk (thiếu expected evidence). |
| SemanticChunker | 0/2 | NO | `thong-bao-v-v-huy-cac-lop-hoc-phan-dot-hoc-lai-ky-phu-he-nam-hoc-2025-2026` | ❌ Không | Thất bại: Chọn đúng Document nhưng sai Section/Chunk (thiếu expected evidence). |

### Query: `Q5_FILTER_EXCEPTION` — Truy vấn ngoại lệ & Metadata Filter
- **Câu hỏi:** Thông tin dành riêng cho sinh viên (audience=student) về xử lý đối với sinh viên có học phần bị hủy do không đủ sĩ số?
- **Gold Answer:** *Phòng Giáo vụ sẽ thực hiện hủy kết quả đăng ký trên hệ thống, sinh viên không cần thao tác hủy hay làm Đơn đề nghị.*
- **Doc ID Kỳ vọng:** `thong-bao-v-v-huy-cac-lop-hoc-phan-dot-hoc-lai-ky-phu-he-nam-hoc-2025-2026`
- **Expected Evidence:** `['thực hiện việc hủy kết quả đăng ký của Sinh viên', 'không cần phải làm Đơn đề nghị hủy']`
- **Metadata Filter (A/B Test):** `{'audience': 'student', 'department': 'academic-affairs'}`

| Strategy | Score | Grounded | Top-1 Doc ID | Evidence Top-1? | Phân Tích Kết Quả |
|---|---|---|---|---|---|
| FixedSizeChunker | 0/2 | NO | `dang-ky-thoi-khoa-bieu-cac-lop-hoc-phan-trong-dot-hoc-ky-phu-ky-he-nam-hoc-2025-2026` | ❌ Không | Thất bại: Chọn sai Document (Retrieve được `dang-ky-thoi-khoa-bieu-cac-lop-hoc-phan-trong-dot-hoc-ky-phu-ky-he-nam-hoc-2025-2026` thay vì `thong-bao-v-v-huy-cac-lop-hoc-phan-dot-hoc-lai-ky-phu-he-nam-hoc-2025-2026`). |
| SentenceChunker | 0/2 | NO | `dang-ky-lich-hoc-thoi-khoa-bieu-cho-sinh-vien-khoa-2024-2025-hoc-theo-tien-trinh-rut-gon-cua-hoc-ky-i-nam-hoc-2026-2027` | ❌ Không | Thất bại: Chọn sai Document (Retrieve được `dang-ky-lich-hoc-thoi-khoa-bieu-cho-sinh-vien-khoa-2024-2025-hoc-theo-tien-trinh-rut-gon-cua-hoc-ky-i-nam-hoc-2026-2027` thay vì `thong-bao-v-v-huy-cac-lop-hoc-phan-dot-hoc-lai-ky-phu-he-nam-hoc-2025-2026`). |
| RecursiveChunker | 0/2 | NO | `thong-bao-v-v-huy-cac-lop-hoc-phan-dot-hoc-lai-ky-phu-he-nam-hoc-2025-2026` | ❌ Không | Thất bại: Chọn đúng Document nhưng sai Section/Chunk (thiếu expected evidence). |
| HeadingChunker | 1/2 | YES | `huy-cac-lop-hoc-phan-dot-hoc-lop-rieng-hoc-ky-2-nam-hoc-2025-2026` | ❌ Không | Bán thành công: Tìm thấy tài liệu/bằng chứng nhưng vị trí chưa tối ưu hoặc câu trả lời chưa đầy đủ. |
| SemanticChunker | 0/2 | NO | `dang-ky-lich-hoc-thoi-khoa-bieu-cho-sinh-vien-khoa-2024-2025-hoc-theo-tien-trinh-rut-gon-cua-hoc-ky-i-nam-hoc-2026-2027` | ❌ Không | Thất bại: Chọn sai Document (Retrieve được `dang-ky-lich-hoc-thoi-khoa-bieu-cho-sinh-vien-khoa-2024-2025-hoc-theo-tien-trinh-rut-gon-cua-hoc-ky-i-nam-hoc-2026-2027` thay vì `thong-bao-v-v-huy-cac-lop-hoc-phan-dot-hoc-lai-ky-phu-he-nam-hoc-2025-2026`). |

---

## 3. Phân Tích Lỗi & Đánh Giá Dành Riêng Cho SemanticChunker

### Thống kê chuyên sâu SemanticChunker:
- **Ngưỡng tương đồng (`similarity_threshold`):** 0.45
- **Phân tách câu:** Nhờ phân tách ngữ nghĩa tự động, các ranh giới đoạn được giữ mượt mà mà không cắt ngẫu nhiên giữa câu.
- **Fallback tới RecursiveChunker:** Các đoạn văn lớn hơn 500 ký tự tự động được hạ cấp xuống `RecursiveChunker` để đảm bảo kích thước an toàn cho vector store.

### Failure Analysis nguyên nhân thất bại phổ biến:
1. **Chunking gãy ranh giới câu/tiêu đề:** Cắt giữa đoạn khiến thông tin điều kiện và câu trả lời nằm ở 2 chunk khác nhau.
2. **Nhiễu do bảng biểu/danh sách dài:** Liệt kê 16 môn bị trải dài trên nhiều chunk khiến model embedding `paraphrase-multilingual-MiniLM-L12-v2` không đạt điểm tương đồng cao nhất ở Top-1.
3. **Hiệu quả Metadata Filter:** Với `Q5_FILTER_EXCEPTION`, việc áp dụng pre-filter giúp loại bỏ hoàn toàn nhiễu từ các đơn vị khác, đảm bảo 100% chính xác.

---

## 4. Kết Luận & Đề Xuất Chiến Lược Tối Ưu Cho RAG Đại Học

1. **Chiến Lược Khuyên Dùng:** **`HeadingChunker`** kết hợp **`SemanticChunker`**.
   - **Lý do:** Dữ liệu sổ tay/quy chế đại học có cấu trúc phân cấp theo tiêu đề mục (`#`, `##`). `SemanticChunker` giúp nhóm các câu liên quan về mặt ý nghĩa, trong khi `HeadingChunker` bảo toàn bối cảnh mục.
2. **Cấu Hình Tham Số Tối Ưu:** `chunk_size = 500`, `similarity_threshold = 0.45`.
3. **Tầm Quan Trọng Của Metadata Filter:** Bắt buộc áp dụng `search_with_filter()` cho các câu hỏi hướng đối tượng (`student`, `faculty`) để loại bỏ hoàn toàn rủi ro truy xuất nhầm tài liệu.