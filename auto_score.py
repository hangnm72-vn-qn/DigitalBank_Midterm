"""Ghi điểm Score_0_5 vào raw_data.csv bằng ĐÚNG rubric của scoring.py.

Rubric nằm ở một nơi duy nhất (scoring.py) để hai file không bao giờ lệch nhau.
CUS2/CUS3 (định lượng) để trống; scoring.py sẽ Min-Max hoặc đánh N/A.
"""
from pathlib import Path

import pandas as pd

from scoring import QUANT_INDICATORS, qualitative_score

RAW_FILE = Path(__file__).resolve().parent / "raw_data.csv"

df = pd.read_csv(RAW_FILE, encoding="utf-8-sig")


def auto_assign_score(row):
<<<<<<< HEAD
    indicator = str(row.get("Indicator_ID", "")).strip()
    evidence = str(row.get("Evidence", "")).strip().lower()

    # 1. Tiêu chí định lượng (CUS2, CUS3) để trống để scoring.py chạy Min-Max
    if indicator in QUANT_INDICATORS:
        return "N/A"

    # 2. Trường hợp N/A (Không tìm thấy bằng chứng công khai) -> Trả về None (Để trống ô)
    if not evidence or "not_found_public_evidence" in evidence:
        return "N/A"

    combined = evidence

    # 3. Phân cấp từ Mức 5 xuống Mức 1 theo từ khóa Rubric A.1
    if any(k in combined for k in ["toàn diện", "quy mô lớn", "dẫn đầu", "100%", "cloud-first", "toan dien", "quy mo lon"]):
        return 5.0
    if any(k in combined for k in ["nhiều", "mở rộng", "rộng rãi", "phần lớn", "tích hợp sâu", "tiên tiến", "nhieu", "mo rong"]):
        return 4.0
    if any(k in combined for k in ["hoàn thành", "đã triển khai", "vận hành", "áp dụng", "da trien khai", "van hanh"]):
        return 3.0
    if any(k in combined for k in ["pilot", "thử nghiệm", "thuc nghiem", "trial", "phạm vi nhỏ", "đang ứng dụng"]):
        return 2.0
    if any(k in combined for k in ["kế hoạch", "định hướng", "lộ trình", "dự kiến", "plan", "ke hoach"]):
        return 1.0

    # Nếu có Evidence nhưng là bằng chứng xác nhận CHƯA TRIỂN KHAI -> Gán 0.0
    if any(k in combined for k in ["chưa triển khai", "không triển khai", "ngưng", "dừng", "chua trien khai"]):
        return 0.0

    # Mặc định có Evidence hợp lệ -> Mức 2.0
    return 2.0
=======
    if str(row.get("Indicator_ID", "")).strip() in QUANT_INDICATORS:
        return None
    return qualitative_score(row)[0]

>>>>>>> 8e2475829b75b894667f46862eb35c0b1fea47f6

# Gán lại cột Score_0_5
df["Score_0_5"] = df.apply(auto_assign_score, axis=1)
<<<<<<< HEAD

# Lưu lại file raw_data.csv
df.to_csv("raw_data.csv", index=False, encoding="utf-8-sig")
print("✅ Đã cập nhật xong cột Score_0_5 tách biệt rõ ràng giữa 0.0 và N/A!")
=======
df.to_csv(RAW_FILE, index=False, encoding="utf-8-sig")
print("✅ Đã cập nhật Score_0_5 theo rubric của scoring.py!")
>>>>>>> 8e2475829b75b894667f46862eb35c0b1fea47f6
