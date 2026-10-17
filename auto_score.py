import pandas as pd

df = pd.read_csv("raw_data.csv")

QUANT_INDICATORS = {"CUS2", "CUS3"}

def auto_assign_score(row):
    indicator = str(row.get("Indicator_ID", "")).strip()
    evidence = str(row.get("Evidence", "")).strip().lower()

    # Chỉ tiêu định lượng (CUS2, CUS3) để trống để scoring.py chạy Min-Max
    if indicator in QUANT_INDICATORS:
        return None

    # Nếu không có bằng chứng public -> 0 điểm
    if not evidence or "not_found_public_evidence" in evidence:
        return 0.0

    # CHỈ LẤY NỘI DUNG EVIDENCE ĐỂ SO MỐC NEO (Bỏ qua Raw_Value bị dính chữ "Đã triển khai")
    combined = evidence

    # Phân cấp từ Mức 5 xuống Mức 1 theo từ khóa nổi bật trong Evidence
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

    # Nếu có Evidence nhưng chưa khớp từ khóa chuẩn -> Mặc định chấm Mức 2.0
    return 2.0

df["Score_0_5"] = df.apply(auto_assign_score, axis=1)

# Lưu lại file raw_data.csv (hoặc raw_data_scored.csv)
df.to_csv("raw_data.csv", index=False, encoding="utf-8-sig")
print("✅ Đã cập nhật xong điểm Score_0_5 phân hóa theo đoạn Evidence!")