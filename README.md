# 🏦 DỰ ÁN MÔN HỌC: ĐÁNH GIÁ MỨC ĐỘ CHUYỂN ĐỔI SỐ NGÂN HÀNG (DIGITAL BANKING INDEX - DBI) GIAI ĐOẠN 2021–2025
 
> **Khung tham chiếu:** Bộ tiêu chí đánh giá mức độ chuyển đổi số doanh nghiệp lớn theo Quyết định 1567/QĐ-BKHCN ngày 30/06/2025, được rút gọn còn 24 tiêu chí có thể quan sát từ nguồn dữ liệu công khai.

---

## 📌 1. VAI TRÒ VÀ MỤC TIÊU CỦA DỰ ÁN

Dự án được xây dựng nhằm thu thập, chuẩn hóa, chấm điểm và trực quan hóa mức độ chuyển đổi số (CĐS) của 5 ngân hàng thương mại Việt Nam gồm **VCB, TCB, VPBank, BIDV và ACB** trong giai đoạn 2021–2025, dựa hoàn toàn trên **nguồn dữ liệu công khai (Public Data)**.

### Mục tiêu cốt lõi

- **Đánh giá đa chiều:** Đo lường chỉ số Digital Banking Index (DBI) thông qua 6 trụ cột: Khách hàng (Customer), Chiến lược (Strategy), Công nghệ (Technology), Vận hành (Operations), Văn hóa (Culture) và Dữ liệu (Data).
- **Theo dõi tiến trình 5 năm (2021–2025):** Xác định ngân hàng dẫn đầu, ngân hàng cải thiện nhanh nhất và phân tích điểm mạnh, điểm yếu của từng ngân hàng theo từng năm.
- **Minh bạch và có thể kiểm chứng (Evidence-based):** Mọi điểm số định tính (0–5) và dữ liệu định lượng đều gắn với bằng chứng trích dẫn từ Báo cáo thường niên (BCTN), Báo cáo phát triển bền vững (PTBV), Báo cáo tài chính (BCTC), tài liệu Quan hệ nhà đầu tư (IR) và thông cáo chính thức.
- **Trực quan hóa tương tác:** Xây dựng Dashboard bằng Streamlit và Plotly, hỗ trợ tra cứu bảng xếp hạng, theo dõi xu hướng, so sánh các trụ cột và truy xuất bằng chứng gốc.

---

## 🏗️ 2. KIẾN TRÚC HỆ THỐNG VÀ PHÂN CÔNG THÀNH VIÊN

Dự án vận hành theo pipeline khép kín, từ thu thập dữ liệu thô, xử lý và chấm điểm đến trực quan hóa kết quả.

### 2.1. Cấu trúc thư mục

```text
DigitalBank_Midterm/
│
├── sources/                   # Tài liệu PDF nguồn công khai, phân loại theo ngân hàng/năm
│
├── data_collection.py         # [TV1] Trích xuất PDF, tìm từ khóa và tổng hợp bằng chứng ứng viên
├── candidate_evidences.csv    # [TV1] Các đoạn văn bản ứng viên chứa từ khóa
├── raw_data.csv               # [TV1] Dữ liệu gốc và bằng chứng đã xác nhận thủ công
├── data_quality_raw.csv       # [TV1] Đánh giá chất lượng dữ liệu thô ban đầu
│
├── scoring.py                 # [TV2] Làm sạch, chuẩn hóa và tính điểm DBI
├── cleaned_data.csv           # [TV2] Dữ liệu sau làm sạch và chuẩn hóa mã chỉ tiêu
├── scored_data.csv            # [TV2] Điểm chi tiết 24 tiêu chí kèm căn cứ chấm điểm
├── final_scores.csv           # [TV2] Điểm 6 trụ cột, Digital Score và thứ hạng
├── data_quality.csv           # [TV2] Báo cáo chất lượng dữ liệu
├── sensitivity_check.csv      # [TV2] Kiểm tra độ nhạy thứ hạng
│
├── dashboard.py               # [TV3] Mã nguồn chính của Dashboard Streamlit
├── charts.py                  # [TV3] Các biểu đồ tương tác sử dụng Plotly
│
├── requirements.txt           # Danh sách thư viện phụ thuộc
└── README.md                  # Tài liệu hướng dẫn và thuyết minh dự án
```

### 2.2. Phân công và chức năng các thành phần

**1. `data_collection.py` — Thành viên 1: Data Collection**

- Quét các tài liệu trong thư mục `sources/`.
- Trích xuất văn bản từ PDF và tìm kiếm từ khóa liên quan đến các tiêu chí chuyển đổi số.
- Xuất các đoạn văn bản ứng viên vào `candidate_evidences.csv` để đối chiếu.
- Hỗ trợ xác minh thủ công và tổng hợp dữ liệu cuối cùng vào `raw_data.csv`.
- Đánh giá chất lượng dữ liệu thô và xuất báo cáo `data_quality_raw.csv`.

**2. `scoring.py` — Thành viên 2: Scoring & Ranking**

- Đọc dữ liệu từ `raw_data.csv`.
- Làm sạch dữ liệu, chuẩn hóa mã chỉ tiêu và xử lý các giá trị thiếu (N/A).
- Áp dụng Rubric chấm điểm từ 0–5 cho 22 tiêu chí định tính.
- Chuẩn hóa Min–Max trên 25 quan sát cho hai tiêu chí định lượng CUS2 và CUS3.
- Tổng hợp điểm 6 trụ cột, tính Digital Score và xếp hạng các ngân hàng theo từng năm.
- Xuất các báo cáo `cleaned_data.csv`, `scored_data.csv`, `final_scores.csv`, `data_quality.csv` và `sensitivity_check.csv`.

**3. `dashboard.py` và `charts.py` — Thành viên 3: Dashboard & Visualization**

- Xây dựng giao diện web bằng Streamlit.
- Sử dụng Plotly để tạo các biểu đồ tương tác như biểu đồ xu hướng, biểu đồ radar và heatmap.
- Hiển thị bảng xếp hạng, điểm số tổng hợp và kết quả so sánh giữa các ngân hàng.
- Hỗ trợ tra cứu bằng chứng gốc và thông tin chất lượng dữ liệu.
- Chuẩn hóa font chữ Times New Roman và định dạng giao diện nhằm bảo đảm tính nhất quán, dễ đọc.
- Chỉ đọc các tập dữ liệu đã được xử lý và chốt, không thực hiện lại quy trình thu thập hoặc chấm điểm.

---

## 🛠️ 3. YÊU CẦU MÔI TRƯỜNG VÀ CÀI ĐẶT

### 3.1. Yêu cầu hệ thống

- **Python:** Phiên bản 3.9–3.12.
- **Hệ điều hành:** Windows 10/11, macOS hoặc Linux.
- **Các thư viện:** Được liệt kê trong file `requirements.txt`.

### 3.2. Hướng dẫn cài đặt từ môi trường sạch

#### Bước 1: Clone repository từ GitHub

```bash
git clone <URL_GITHUB_CUA_NHOM>
cd DigitalBank_Midterm
```

Thay `<URL_GITHUB_CUA_NHOM>` bằng đường dẫn repository thực tế của nhóm.

#### Bước 2: Tạo và kích hoạt môi trường ảo

**Trên Windows (PowerShell/CMD):**

```bash
python -m venv venv
.\venv\Scripts\activate
```

**Trên macOS/Linux:**

```bash
python3 -m venv venv
source venv/bin/activate
```

#### Bước 3: Cài đặt các thư viện phụ thuộc

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

---

## 🚀 4. HƯỚNG DẪN VẬN HÀNH DỰ ÁN

Dự án tuân thủ trình tự vận hành gồm ba bước: thu thập bằng chứng, tính toán điểm số và khởi chạy Dashboard.

### Bước 1: Trích xuất và tổng hợp bằng chứng

Chạy lệnh sau khi bổ sung tài liệu PDF mới hoặc cần tạo lại tập bằng chứng ứng viên:

```bash
python data_collection.py
```

**Đầu ra dự kiến:**

- `candidate_evidences.csv`: Các đoạn văn bản ứng viên được trích xuất từ tài liệu.
- `raw_data.csv`: Dữ liệu đã được xác minh và tổng hợp thủ công.
- `data_quality_raw.csv`: Báo cáo chất lượng dữ liệu thô, nếu được triển khai trong mã nguồn.

**Lưu ý:** Các đoạn văn bản được trích xuất tự động chỉ là bằng chứng ứng viên. Cần đối chiếu tài liệu gốc trước khi xác nhận và sử dụng để chấm điểm.

### Bước 2: Tính toán điểm số và xếp hạng

Sau khi dữ liệu trong `raw_data.csv` đã được xác minh, chạy:

```bash
python scoring.py
```

**Đầu ra dự kiến:**

- `cleaned_data.csv`: Dữ liệu đã làm sạch.
- `scored_data.csv`: Điểm số chi tiết của 24 tiêu chí.
- `final_scores.csv`: Điểm tổng hợp 6 trụ cột, Digital Score và thứ hạng.
- `data_quality.csv`: Báo cáo chất lượng dữ liệu sau xử lý.
- `sensitivity_check.csv`: Báo cáo kiểm tra độ nhạy của thứ hạng.

Các file đầu ra được cập nhật theo logic xử lý được triển khai trong `scoring.py`.

### Bước 3: Khởi chạy Dashboard

Sau khi hoàn tất xử lý dữ liệu, chạy:

```bash
streamlit run dashboard.py
```

Ứng dụng sẽ hiển thị địa chỉ truy cập trên terminal. Thông thường, giao diện có thể được mở tại:

```text
http://localhost:8501
```

Dashboard sử dụng các tập dữ liệu đã xử lý để trực quan hóa kết quả, hỗ trợ tra cứu và so sánh mức độ chuyển đổi số của các ngân hàng trong giai đoạn 2021–2025.

---

## 📊 5. PHƯƠNG PHÁP CHẤM ĐIỂM VÀ TỔNG HỢP DBI

### 5.1. Phạm vi đánh giá

- **Đối tượng:** 5 ngân hàng thương mại Việt Nam: VCB, TCB, VPBank, BIDV và ACB.
- **Thời gian:** 2021–2025.
- **Quy mô dữ liệu:** 25 quan sát ngân hàng–năm.
- **Số lượng tiêu chí:** 24 tiêu chí thuộc 6 trụ cột chuyển đổi số.
- **Nguồn dữ liệu:** Báo cáo thường niên, báo cáo phát triển bền vững, báo cáo tài chính, tài liệu IR và các thông tin chính thức được công bố công khai.

### 5.2. Cơ chế chấm điểm

**Đối với 22 tiêu chí định tính:**

Sử dụng Rubric với thang điểm từ 0 đến 5. Mỗi mức điểm cần có mô tả điều kiện đánh giá và căn cứ bằng chứng tương ứng.

**Đối với 2 tiêu chí định lượng CUS2 và CUS3:**

Áp dụng phương pháp chuẩn hóa Min–Max trên tập 25 quan sát ngân hàng–năm theo quy tắc được quy định trong `scoring.py`.

Công thức chuẩn hóa Min–Max:

\[
X_{\text{norm}} =
\frac{X-X_{\min}}{X_{\max}-X_{\min}}
\times 5
\]

Trong đó:

- \(X\): Giá trị quan sát ban đầu.
- \(X_{\min}\): Giá trị nhỏ nhất trong tập quan sát.
- \(X_{\max}\): Giá trị lớn nhất trong tập quan sát.
- \(X_{\text{norm}}\): Giá trị sau chuẩn hóa trên thang điểm 0–5.

**Lưu ý:** Công thức trên áp dụng khi tiêu chí có chiều tác động thuận và \(X_{\max} \ne X_{\min}\). Trường hợp tiêu chí có chiều tác động nghịch hoặc các giá trị quan sát bằng nhau cần được xử lý theo quy tắc riêng được xác định trước.

### 5.3. Tổng hợp điểm số

Điểm của từng ngân hàng được tổng hợp theo 6 trụ cột:

1. Customer — Khách hàng.
2. Strategy — Chiến lược.
3. Technology — Công nghệ.
4. Operations — Vận hành.
5. Culture — Văn hóa.
6. Data — Dữ liệu.

Digital Score được tính dựa trên phương pháp tổng hợp và trọng số đã xác định trong mô hình chấm điểm. Thứ hạng được xác định theo Digital Score của từng ngân hàng trong từng năm.

Để bảo đảm khả năng kiểm chứng, các tiêu chí, trọng số, cách xử lý N/A và quy tắc chuẩn hóa cần được quy định nhất quán trong mã nguồn và tài liệu phương pháp luận.

---

## ⚠️ 6. HẠN CHẾ PHƯƠNG PHÁP VÀ LƯU Ý DỮ LIỆU

### 6.1. Bản chất của chỉ số DBI

DBI trong nghiên cứu này là chỉ số đánh giá được xây dựng dựa trên dữ liệu công khai (Public-Data-Based Index). Chỉ số phục vụ mục đích nghiên cứu, so sánh và theo dõi xu hướng chuyển đổi số; **không phải chỉ số đánh giá nội bộ chính thức của các ngân hàng**.

### 6.2. Diễn giải điểm 0

Đối với tiêu chí định tính, điểm 0 phản ánh việc **không tìm thấy bằng chứng công khai đáp ứng tiêu chí trong phạm vi nguồn dữ liệu khảo sát của năm tương ứng**.

Điểm 0 không đồng nghĩa với việc ngân hàng chắc chắn không triển khai năng lực hoặc hoạt động đó.

### 6.3. Xử lý dữ liệu thiếu

Các trường hợp N/A cần được phân biệt rõ với điểm 0. Việc xử lý dữ liệu thiếu có thể ảnh hưởng đến điểm tổng hợp và thứ hạng, do đó cần công bố phương pháp xử lý để bảo đảm tính minh bạch và khả năng so sánh.

### 6.4. Tính chất dữ liệu của Dashboard

Dashboard phản ánh dữ liệu tĩnh theo các mốc báo cáo năm đã được thu thập, xác minh và chốt. Hệ thống không phản ánh dữ liệu thời gian thực (real-time).

Kết quả phụ thuộc vào phạm vi tài liệu công khai, chất lượng bằng chứng, thời điểm công bố và phương pháp chấm điểm được áp dụng.

### 6.5. Kiểm tra độ nhạy

Báo cáo `sensitivity_check.csv` được sử dụng để đánh giá sự thay đổi của thứ hạng khi loại bỏ hai tiêu chí định lượng CUS2 và CUS3 theo kịch bản kiểm tra đã thiết kế.

Kết quả giúp xác định mức độ phụ thuộc của thứ hạng vào các tiêu chí định lượng và hỗ trợ diễn giải kết quả thận trọng hơn.

---


## 👥 7. ĐÓNG GÓP VÀ PHÁT TRIỂN

Dự án được tổ chức theo ba nhóm công việc chính:

- **Data Collection:** Thu thập, trích xuất, xác minh và chuẩn hóa bằng chứng.
- **Scoring & Ranking:** Xử lý dữ liệu, áp dụng Rubric, tính điểm và kiểm tra độ nhạy.
- **Dashboard & Visualization:** Phát triển giao diện tương tác và trực quan hóa kết quả.

Mọi thay đổi đối với cấu trúc dữ liệu, mã chỉ tiêu, Rubric hoặc phương pháp tính điểm cần được đồng bộ giữa các thành phần của hệ thống để bảo đảm tính nhất quán của kết quả.

---

## 📌 8. TUYÊN BỐ VỀ TÍNH MINH BẠCH

Nghiên cứu ưu tiên khả năng truy xuất nguồn, tính nhất quán của phương pháp và khả năng kiểm chứng kết quả. Mọi nhận định về mức độ chuyển đổi số cần được diễn giải trong phạm vi dữ liệu công khai đã thu thập, không thay thế cho đánh giá nội bộ hoặc kiểm toán độc lập đối với các ngân hàng.

**Digital Banking Index (DBI) 2021–2025 — Public Data, Evidence-based Scoring, Transparent Comparison.**
