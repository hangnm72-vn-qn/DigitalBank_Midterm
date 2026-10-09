# Giai Đạn 1: Thu Thập Dữ Liệu & Trích Xuất Bằng Chứng (Data Collection & Evidence Extraction)

## 📌 Phân công nhiệm vụ
- **Thành viên thực hiện:** Hằng 
- **Nhiệm vụ:** Xây dựng danh mục nguồn tài liệu, viết script quét tự động file PDF báo cáo ngân hàng, trích xuất bằng chứng thô cho 24 tiêu chí Chuyển đổi số.

## 📁 Cấu trúc thư mục
- `sources/`: Lưu trữ các BCTN, BCTC của 5 ngân hàng (ACB, BIDV, TCB, VCB, VPBank) từ 2021-2025.
- `source_catalog.csv`: Nhật ký quản lý nguồn và đường dẫn tải tài liệu.
- `data_collection.py`: Script Python tự động quét từ khóa và trích xuất bằng chứng từ file PDF.
- `raw_data.csv`: File dữ liệu thô chuẩn 13 cột (600 dòng quan sát).
- `data_quality_raw.csv`: Báo cáo đánh giá chất lượng và độ phủ bằng chứng thô.

## 🚀 Cách chạy code
1. Cài đặt thư viện: `pip install pandas pypdf`
2. Chạy quét dữ liệu: `python data_collection.py`
3. Kiểm tra chất lượng dữ liệu: `python data_quality_raw.py`