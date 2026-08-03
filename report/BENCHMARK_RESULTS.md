# Báo Cáo Đánh Giá So Sánh Chiến Lược Chunking (Benchmark Report)

> Được tạo tự động vào lúc: 2026-08-03 11:17:47

## 1. Tổng Quan Hiệu Năng Các Chiến Lược

| Chiến Lược (Strategy) | Kích Thước / Tham Số | Tổng Chunks | Avg Chunks/Doc | Độ Dài TB (chars) | Thời Gian Indexing (s) | Thời Gian Retrieval (s) |
|---|---|---|---|---|---|---|
| **FixedSizeChunker** | `chunk_size=500, overlap=50` | 54 | 4.91 | 471.7 | 0.0261s | 0.0072s |
| **SentenceChunker** | `max_sentences_per_chunk=3` | 37 | 3.36 | 627.8 | 0.0191s | 0.0042s |
| **RecursiveChunker** | `chunk_size=500, separators=['\n\n', '\n', '. ', ' ']` | 60 | 5.45 | 387.1 | 0.0199s | 0.0066s |
| **HeadingChunker** | `chunk_size=500, heading_split=True` | 60 | 5.45 | 457.4 | 0.0177s | 0.0063s |

## 2. Chi Tiết Kết Quả Truy Xuất Theo 5 Benchmark Queries

### Query: `Q1_NUMERICAL` — Truy vấn số liệu
**Câu hỏi:** Số lượng lớp học phần bị hủy do số lượng sinh viên đăng ký thời khóa biểu không đủ điều kiện mở lớp trong đợt học lại kỳ phụ năm 2025-2026 là bao nhiêu?
**Gold Answer:** *Hủy 16 lớp học phần do số lượng sinh viên đăng ký thời khóa biểu không đủ điều kiện mở lớp.*
**Kỳ vọng Doc ID:** `thong-bao-v-v-huy-cac-lop-hoc-phan-dot-hoc-lai-ky-phu-he-nam-hoc-2025-2026`

| Strategy | Top-1 Score | Top-1 Doc ID | Top-1 Chunk Index | Top-1 Preview |
|---|---|---|---|---|
| FixedSizeChunker | 0.2843 | `huy-cac-lop-hoc-phan-dot-hoc-lop-rieng-hoc-ky-2-nam-hoc-2025-2026` | 1 | g ký học phần  26/03/2026  giaovu  Kính gửi: Các lớp sinh viên Đại học chính quy cơ sở đào tạo Hà Nộ... |
| SentenceChunker | 0.2918 | `k3-course-registration` | 1 | Một học phần có thể yêu cầu học phần tiên quyết; sinh viên cần kiểm tra điều kiện trước khi xác nhận... |
| RecursiveChunker | 0.4035 | `dang-ky-lich-hoc-thoi-khoa-bieu-cho-sinh-vien-khoa-2024-2025-hoc-theo-tien-trinh-rut-gon-cua-hoc-ky-i-nam-hoc-2026-2027` | 3 | Các sinh viên đã đăng ký nguyện vọng học theo tiến trình rút gọn (danh sách sinh viên kèm theo)  Tổ ... |
| HeadingChunker | 0.3022 | `dang-ky-lich-hoc-thoi-khoa-bieu-cho-sinh-vien-khoa-2024-2025-hoc-theo-tien-trinh-rut-gon-cua-hoc-ky-i-nam-hoc-2026-2027` | 7 | # Đăng ký lịch học (thời khoá biểu) cho sinh viên khoá 2024, 2025 học theo tiến trình rút gọn của họ... |

### Query: `Q2_CONDITION` — Truy vấn điều kiện
**Câu hỏi:** Điều kiện để sinh viên đại học chính quy khóa 2024, 2025 được đăng ký lịch học theo tiến trình rút gọn học kỳ I năm học 2026-2027 là gì?
**Gold Answer:** *Sinh viên đã đăng ký nguyện vọng học theo tiến trình rút gọn, không được đăng ký các môn ngoài tiến trình rút gọn, không đăng ký học lại/học cải thiện trong thời gian này và phải đảm bảo các điều kiện tiên quyết của học phần.*
**Kỳ vọng Doc ID:** `dang-ky-lich-hoc-thoi-khoa-bieu-cho-sinh-vien-khoa-2024-2025-hoc-theo-tien-trinh-rut-gon-cua-hoc-ky-i-nam-hoc-2026-2027`

| Strategy | Top-1 Score | Top-1 Doc ID | Top-1 Chunk Index | Top-1 Preview |
|---|---|---|---|---|
| FixedSizeChunker | 0.2950 | `thong-bao-v-v-huy-cac-lop-hoc-phan-dot-hoc-lai-ky-phu-he-nam-hoc-2025-2026` | 3 |  13 MUL13108 Ngôn ngữ lập trình Java  14 MUL1314 Kỹ thuật quay phim  15 MUL1423 Kịch bản đa phương t... |
| SentenceChunker | 0.2531 | `dang-ky-lich-hoc-thoi-khoa-bieu-cho-sinh-vien-khoa-2024-2025-hoc-theo-tien-trinh-rut-gon-cua-hoc-ky-i-nam-hoc-2026-2027` | 2 | Bước 3: SV đăng ký đầy đủ các lớp học phần theo tiến trình rút gọn của kỳ 1 năm học 2026-2027. Lưu ý... |
| RecursiveChunker | 0.3616 | `to-chuc-hoc-hoc-ky-phu-ky-he-nam-hoc-2025-2026` | 4 | Sinh viên nếu không đăng ký nguyện vọng ở bước 1 sẽ không được đăng ký Thời khóa biểu ở bước 3.  Sin... |
| HeadingChunker | 0.2878 | `tap-trung-pho-bien-ke-hoach-dang-ky-mon-hoc-ky-i-nam-hoc-2026-2027` | 6 | # Tập trung phổ biến kế hoạch đăng ký môn học kỳ I năm học 2026-2027 6. Đăng ký lịch học (Thời khóa ... |

### Query: `Q3_PROCESS` — Truy vấn quy trình
**Câu hỏi:** Quy trình các bước sinh viên thực hiện đăng ký nguyện vọng học vượt học kỳ I năm học 2026-2027 trên hệ thống QLĐT?
**Gold Answer:** *Bước 1: Đăng nhập Hệ thống QLĐT và chọn chức năng 'Đăng ký nguyện vọng'. Bước 2: Nhập mã học phần theo CTĐT học vượt đã được công bố. Bước 3: Nhấn nút 'Đăng ký' để lưu kết quả.*
**Kỳ vọng Doc ID:** `to-chuc-dang-ky-hoc-vuot-hoc-ky-i-nam-hoc-2026-2027-doi-voi-sinh-vien-khoa-2024-2025`

| Strategy | Top-1 Score | Top-1 Doc ID | Top-1 Chunk Index | Top-1 Preview |
|---|---|---|---|---|
| FixedSizeChunker | 0.2956 | `dieu-chinh-lich-dang-ky-hoc-lai-hoc-cai-thien-hoc-2-van-bang-tren-qldt-hoc-ky-2-nam-hoc-2025-2026` | 2 | 0 ngày 09/01/2026 đến 24h00 ngày 14/01/2026 trên hệ thống QLĐT: https://qldt.ptit.edu.vn  2. Đối tượ... |
| SentenceChunker | 0.1566 | `k3-course-registration` | 1 | Một học phần có thể yêu cầu học phần tiên quyết; sinh viên cần kiểm tra điều kiện trước khi xác nhận... |
| RecursiveChunker | 0.2046 | `lich-nghi-tet-duong-lich-nam-2026-va-dieu-chinh-lich-thi-lich-dang-ky-hoc-phan` | 0 | # Lịch nghỉ Tết Dương lịch năm 2026 và điều chỉnh lịch thi, lịch đăng ký học phần  Lịch nghỉ Tết Dươ... |
| HeadingChunker | 0.2420 | `huy-cac-lop-hoc-phan-dot-hoc-lop-rieng-hoc-ky-2-nam-hoc-2025-2026` | 2 | # Hủy các lớp học phần đợt học lớp riêng, học kỳ 2 năm học 2025-2026 3 SKD1102 Kỹ năng làm việc nhóm... |

### Query: `Q4_ENUMERATION` — Truy vấn liệt kê
**Câu hỏi:** Liệt kê danh sách các môn học bị hủy trong đợt học lại kỳ phụ (hè) năm học 2025-2026?
**Gold Answer:** *Tiếng Anh (Course 1 _CLC), Thị giác máy tính, Cơ sở đo lường điện tử, Truyền thông số, Marketing căn bản, Marketing công nghiệp, Nguyên lý kế toán, Xác suất thống kê, Toán rời rạc 2, Luật xa gần, CAD/CAM, Kiến trúc máy tính, Ngôn ngữ lập trình Java, Kỹ thuật quay phim, Kịch bản đa phương tiện, Vật lý 3 và thí nghiệm.*
**Kỳ vọng Doc ID:** `thong-bao-v-v-huy-cac-lop-hoc-phan-dot-hoc-lai-ky-phu-he-nam-hoc-2025-2026`

| Strategy | Top-1 Score | Top-1 Doc ID | Top-1 Chunk Index | Top-1 Preview |
|---|---|---|---|---|
| FixedSizeChunker | 0.2906 | `dang-ky-thoi-khoa-bieu-cac-lop-hoc-phan-trong-dot-hoc-ky-phu-ky-he-nam-hoc-2025-2026` | 2 | học, cụ thể như sau:  Danh sách và thời khóa biểu các học phần có bố trí mở lớp, không mở lớp, các h... |
| SentenceChunker | 0.1955 | `dang-ky-thoi-khoa-bieu-cac-lop-hoc-phan-trong-dot-hoc-ky-phu-ky-he-nam-hoc-2025-2026` | 2 | Sinh viên phải cân nhắc kỹ trước khi đăng ký mỗi học phần để tự đảm bảo thời gian cho các nội dung h... |
| RecursiveChunker | 0.2347 | `lich-nghi-tet-duong-lich-nam-2026-va-dieu-chinh-lich-thi-lich-dang-ky-hoc-phan` | 3 | Đề nghị Ban cán sự các lớp phổ biến cho sinh viên lớp mình nắm rõ và nghiêm túc thực hiện. Trong thờ... |
| HeadingChunker | 0.2297 | `dang-ky-thoi-khoa-bieu-cac-lop-hoc-phan-trong-dot-hoc-ky-phu-ky-he-nam-hoc-2025-2026` | 2 | # Đăng ký thời khóa biểu các lớp học phần trong đợt học kỳ phụ (kỳ hè) năm học 2025-2026 Danh sách v... |

### Query: `Q5_FILTER_EXCEPTION` — Truy vấn ngoại lệ & Metadata Filter
**Câu hỏi:** Thông tin dành riêng cho sinh viên (audience=student) về xử lý đối với sinh viên có học phần bị hủy do không đủ sĩ số?
**Gold Answer:** *Phòng Giáo vụ sẽ thực hiện hủy kết quả đăng ký của Sinh viên trên hệ thống, sinh viên không cần thực hiện thao tác hủy học phần hay làm Đơn đề nghị hủy.*
**Kỳ vọng Doc ID:** `thong-bao-v-v-huy-cac-lop-hoc-phan-dot-hoc-lai-ky-phu-he-nam-hoc-2025-2026`
**Metadata Filter:** `{'audience': 'student', 'department': 'academic-affairs'}`

| Strategy | Top-1 Score | Top-1 Doc ID | Top-1 Chunk Index | Top-1 Preview |
|---|---|---|---|---|
| FixedSizeChunker | 0.3334 | `dieu-chinh-lich-dang-ky-hoc-lai-hoc-cai-thien-hoc-2-van-bang-tren-qldt-hoc-ky-2-nam-hoc-2025-2026` | 0 | # Điều chỉnh lịch đăng ký học lại, học cải thiện, học 2 văn bằng trên QLĐT học kỳ 2 năm học 2025-202... |
| SentenceChunker | 0.2605 | `to-chuc-hoc-hoc-ky-phu-ky-he-nam-hoc-2025-2026` | 1 | Thời gian đăng ký: từ 12h ngày 15/05/2026 đến 24h ngày 19/05/2026. Bước 2: Xây dựng thời khóa biểu  ... |
| RecursiveChunker | 0.2492 | `to-chuc-hoc-hoc-ky-phu-ky-he-nam-hoc-2025-2026` | 0 | # Tổ chức học học kỳ phụ (kỳ hè) năm học 2025-2026  Tổ chức học học kỳ phụ (kỳ hè) năm học 2025-2026... |
| HeadingChunker | 0.2907 | `dang-ky-thoi-khoa-bieu-cac-lop-hoc-phan-trong-dot-hoc-ky-phu-ky-he-nam-hoc-2025-2026` | 4 | # Đăng ký thời khóa biểu các lớp học phần trong đợt học kỳ phụ (kỳ hè) năm học 2025-2026 Cách đăng k... |

## 3. Nhận Xét Ưu Nhược Điểm Các Chiến Lược

- **FixedSizeChunker (Cố định):** Đơn giản, độ dài đồng đều nhưng dễ làm gãy ngữ cảnh của câu và section.
- **SentenceChunker (Theo câu):** Bảo toàn cấu trúc câu tốt, tuy nhiên kích thước chunk không ổn định do phụ thuộc độ dài đoạn văn.
- **RecursiveChunker (Đệ quy):** Cân bằng xuất sắc giữa việc giữ toàn vẹn đoạn văn/câu và đảm bảo ranh giới kích thước tối đa.
- **HeadingChunker (Domain-specific):** Giữ lại tiêu đề mục ngữ cảnh học vụ K3 trên từng chunk, tối ưu nhất cho bài toán tra cứu quy định đại học.