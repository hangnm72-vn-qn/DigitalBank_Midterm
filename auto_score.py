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
    if str(row.get("Indicator_ID", "")).strip() in QUANT_INDICATORS:
        return None
    return qualitative_score(row)[0]


df["Score_0_5"] = df.apply(auto_assign_score, axis=1)
df.to_csv(RAW_FILE, index=False, encoding="utf-8-sig")
print("✅ Đã cập nhật Score_0_5 theo rubric của scoring.py!")