# 🏦 Đánh giá mức độ chuyển đổi số ngân hàng (Digital Banking Index – DBI) 2021–2025

> **Khung tham chiếu:** Bộ tiêu chí đánh giá mức độ chuyển đổi số doanh nghiệp lớn theo Quyết định 1567/QĐ-BKHCN ngày 30/06/2025, rút gọn còn 24 tiêu chí có thể quan sát từ nguồn dữ liệu công khai.
>
> **Lưu ý:** Đây là **chỉ số rút gọn dựa trên dữ liệu công khai (public-data-based DBI)**, không phải DBI chính thức.

---

## 1. Giới thiệu

Dự án thu thập, chuẩn hóa, chấm điểm và trực quan hóa mức độ chuyển đổi số của 5 ngân hàng **VCB, TCB, VPBank, BIDV, ACB** trong giai đoạn **2021–2025**, chỉ dựa trên tài liệu công khai (BCTN, PTBV, BCTC, IR, thông cáo chính thức).

- **6 trụ cột:** Khách hàng (Customer), Chiến lược (Strategy), Công nghệ (Technology), Vận hành (Operations), Văn hóa (Culture), Dữ liệu (Data).
- **24 tiêu chí:** 22 tiêu chí định tính (chấm 0–5 theo rubric) và 2 tiêu chí định lượng CUS2, CUS3 (chuẩn hóa Min–Max).
- **Có thể kiểm chứng:** mỗi điểm số gắn với bằng chứng trích dẫn, nguồn và số trang.

---

## 2. Cấu trúc thư mục

```text
DigitalBank_Midterm/
│
├── sources/                   # [TV1] PDF nguồn công khai, theo cấu trúc Bank/Year
│
├── data_collection.py         # [TV1] Trích PDF, tìm từ khóa, xuất bằng chứng ứng viên
├── candidate_evidences.csv    # [TV1] Đoạn văn bản ứng viên
├── raw_data.csv               # [TV1] Dữ liệu gốc đã xác nhận thủ công
├── source_catalog.csv         # [TV1] Danh mục nguồn theo ngân hàng/năm
├── data_quality_raw.csv       # [TV1] Chất lượng dữ liệu thô
│
├── scoring.py                 # [TV2] Làm sạch, chấm điểm, xếp hạng
├── cleaned_data.csv           # [TV2] Dữ liệu sau làm sạch
├── scored_data.csv            # [TV2] Điểm 24 tiêu chí kèm căn cứ chấm
├── final_scores.csv           # [TV2] Điểm 6 trụ cột, Digital Score, Rank
├── data_quality.csv           # [TV2] Chất lượng dữ liệu sau xử lý
├── sensitivity_check.csv      # [TV2] Kiểm tra độ nhạy (bỏ CUS2, CUS3)
│
├── dashboard.py               # [TV3] Dashboard (Dash + Plotly)
├── charts.py                  # [TV3] Hàm vẽ biểu đồ dùng cho báo cáo
├── assets/
│   └── style.css              # [TV3] Giao diện sáng/tối của dashboard
│
├── requirements.txt           # Thư viện phụ thuộc
└── README.md
```

---

## 3. Cài đặt từ môi trường sạch

**Yêu cầu:** Python 3.9–3.12, Windows/macOS/Linux, trình duyệt hiện đại (Chrome, Edge, Firefox).

**Bước 1. Lấy mã nguồn**

```bash
git clone <URL_GITHUB_CUA_NHOM>
cd DigitalBank_Midterm
```

**Bước 2. Tạo và kích hoạt môi trường ảo**

```bash
# Windows (PowerShell)
python -m venv venv
.\venv\Scripts\Activate.ps1

# Windows (CMD)
venv\Scripts\activate.bat

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

**Bước 3. Cài thư viện**

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

> Nếu chạy `data_collection.py`, mở `requirements.txt` và bỏ dấu `#` ở thư viện đọc PDF mà file đó dùng, rồi cài lại.

---

## 4. Vận hành

Thứ tự: **thu thập → chấm điểm → dashboard**. Nếu chỉ muốn xem kết quả và các file CSV đã được chốt, bỏ qua bước 1–2 và chạy thẳng bước 3.

**Bước 1. Thu thập bằng chứng** (khi có PDF mới)

```bash
python data_collection.py
```

Kết quả là `candidate_evidences.csv`. Đoạn trích tự động chỉ là **bằng chứng ứng viên**: phải đối chiếu tài liệu gốc và xác nhận thủ công vào `raw_data.csv` trước khi chấm điểm.

**Bước 2. Chấm điểm và xếp hạng**

```bash
python scoring.py
```

Tạo `cleaned_data.csv`, `scored_data.csv`, `final_scores.csv`, `data_quality.csv`, `sensitivity_check.csv`.

**Bước 3. Chạy dashboard**

```bash
python dashboard.py
```

Mở trình duyệt tại **http://127.0.0.1:8050**. Nhấn `Ctrl + C` trong terminal để dừng.

Khi khởi động, terminal in danh sách cột của `final_scores.csv` và thông báo `[OK]` hoặc `[CẢNH BÁO]` về việc dữ liệu có khớp giữa `final_scores.csv` và `scored_data.csv` hay không. Hãy đọc các dòng này sau mỗi lần cập nhật dữ liệu.

---

## 5. Dashboard

Dashboard chỉ **đọc** `final_scores.csv`, `scored_data.csv`, `raw_data.csv` và `data_quality.csv`; không thu thập hay chấm điểm lại. Dữ liệu là các mốc báo cáo năm đã chốt, **không phải realtime**.

**Bộ điều khiển chung (thanh trên cùng):** chọn năm; công tắc *Thử nghiệm loại bỏ CUS2 & CUS3*; công tắc *Chế độ tối*.

| Tab | Nội dung |
|---|---|
| **Overview & Trend** | 5 thẻ ngân hàng kèm hạng và Digital Score; ngân hàng dẫn đầu và tăng nhanh nhất; biểu đồ xu hướng 2021–2025 so với trung bình nhóm; bảng xếp hạng chi tiết |
| **Pillar & Indicator** | Radar 6 trụ cột; biểu đồ cột chồng đóng góp từng trụ cột; so với Trung bình Nhóm Top 5; so sánh đối đầu hai ngân hàng (theo từng năm hoặc cả 5 năm); ma trận điểm từng tiêu chí (lọc theo trụ cột) |
| **Evidence & Quality** | Tra cứu bằng chứng gốc theo ngân hàng/trụ cột/năm/từ khóa; biểu đồ tỷ lệ tìm thấy dữ liệu; số bằng chứng hợp lệ; bảng `data_quality.csv` |
| **Positioning & SWOT** | Bản đồ định vị (vị thế và tốc độ cải thiện); SWOT tương đối so với nhóm 5 ngân hàng |

**Cách hiểu một số chức năng**

- **Kiểm tra độ nhạy:** công tắc tính lại điểm trụ cột, Digital Score và hạng từ `scored_data.csv` khi bỏ CUS2, CUS3. Nếu hai chỉ tiêu này đang N/A thì kết quả trùng kịch bản đầy đủ; dashboard sẽ báo điều này trên thanh trên cùng.
- **Trung bình nhóm:** là trung bình của 5 ngân hàng khảo sát, không đại diện cho toàn ngành ngân hàng Việt Nam.
- **Cột biểu đồ chồng:** mỗi phân đoạn bằng điểm trụ cột chia 6, nên tổng các phân đoạn bằng Digital Score.
- **SWOT:** rút từ dữ liệu công khai khi so với nhóm 5 ngân hàng, mang tính gợi ý định vị, không phải đánh giá nội bộ.
- **Tải ảnh biểu đồ:** di chuột vào biểu đồ, bấm biểu tượng máy ảnh để lưu PNG (độ phân giải gấp đôi).

### Biểu đồ cho báo cáo (`charts.py`)

`charts.py` chứa các hàm vẽ biểu đồ Plotly (font Times New Roman) để đưa vào báo cáo. Ví dụ xuất PNG (cần bỏ dấu `#` ở `kaleido` trong `requirements.txt`):

```python
import pandas as pd
from charts import create_trend_line_chart

final_scores = pd.read_csv("final_scores.csv")
create_trend_line_chart(final_scores).write_image("trend.png", scale=2)
```

---

## 6. Phương pháp chấm điểm

**Phạm vi:** 5 ngân hàng × 5 năm = 25 quan sát; 24 tiêu chí thuộc 6 trụ cột.

**Tiêu chí định tính (22):** chấm 0–5 theo rubric và mốc neo riêng cho từng tiêu chí.

| Điểm | Ý nghĩa |
|---|---|
| 0 | Không tìm thấy bằng chứng công khai trong phạm vi nguồn khảo sát (phản ánh mức độ công bố) |
| 1 | Mới đề cập định hướng hoặc kế hoạch |
| 2 | Thử nghiệm/pilot hoặc phạm vi rất hạn chế |
| 3 | Đã triển khai thực tế, có bằng chứng rõ |
| 4 | Triển khai rộng ở nhiều nghiệp vụ/kênh hoặc có kết quả đáng kể |
| 5 | Quy mô cao, tích hợp sâu, có số liệu/kết quả rõ ràng |

**Tiêu chí định lượng (CUS2, CUS3):** chuẩn hóa Min–Max trên toàn bộ 25 quan sát, chỉ áp dụng khi dữ liệu cùng định nghĩa và đơn vị:

```text
Score = 5 × (Xi − Xmin) / (Xmax − Xmin)
```

**Tổng hợp:**

- Điểm trụ cột = trung bình các tiêu chí hợp lệ của trụ cột theo từng ngân hàng–năm.
- Digital Score = trung bình 6 trụ cột (trọng số bằng nhau).
- Xếp hạng theo Digital Score giảm dần, tính riêng cho từng năm.

**Xử lý dữ liệu thiếu**

- Tiêu chí định tính không có bằng chứng: chấm 0, ghi `NOT_FOUND_PUBLIC_EVIDENCE`.
- Tiêu chí định lượng không công bố hoặc khác định nghĩa: ghi `N/A`, đưa vào Data Quality; không được điền số thay thế.
- Chỉ tiêu định lượng thiếu ở từ 3 ngân hàng trở lên trong cùng năm: không dùng để xếp hạng năm đó.

---

## 7. Hạn chế

- DBI ở đây chỉ phản ánh **mức độ công bố công khai**, không phản ánh toàn bộ năng lực nội bộ. Điểm 0 không đồng nghĩa ngân hàng không triển khai.
- Mức độ công bố thông tin không đồng đều giữa các ngân hàng và các năm, có thể gây thiên lệch.
- Một số dữ liệu định lượng (CUS2, CUS3) chưa đồng nhất định nghĩa nên có thể thiếu.
- Kết quả phụ thuộc rubric và mốc neo; cần phân tích độ nhạy khi diễn giải thứ hạng.

---

## 8. Xử lý sự cố

| Hiện tượng | Cách xử lý |
|---|---|
| `FileNotFoundError: Không tìm thấy ... .csv` | Chạy `dashboard.py` từ thư mục dự án, và chạy `python scoring.py` để tạo đủ file CSV |
| `ModuleNotFoundError: No module named 'dash'` | Chưa kích hoạt môi trường ảo hoặc chưa chạy `pip install -r requirements.txt` |
| `Address already in use` (cổng 8050 bận) | Tắt tiến trình dashboard cũ, hoặc đổi `port=8050` ở cuối `dashboard.py` |
| Giao diện không đổi sau khi sửa CSS | Nhấn `Ctrl + F5` để tải lại, bỏ qua cache |
| Biểu đồ trụ cột trống hoặc N/A | Xem terminal: dòng `[INFO] Cột trong final_scores.csv` và `[CẢNH BÁO]`; kiểm tra `final_scores.csv` đủ 6 cột trụ cột |
| Terminal báo `[CẢNH BÁO] Lệch final_scores.csv vs scored_data.csv` | Hai file không cùng một lần chạy `scoring.py`; chạy lại `scoring.py` rồi khởi động lại dashboard |
| Font chữ không đúng | Cần Internet để tải font Google Fonts; khi offline sẽ dùng font hệ thống |

**Digital Banking Index 2021–2025 — Public data, evidence-based scoring, transparent comparison.**
**Live Demo: https://digital-banking-index.onrender.com/**