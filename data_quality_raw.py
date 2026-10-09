import pandas as pd

# Đọc file raw_data vừa tạo
df = pd.read_csv("raw_data.csv")

# Thống kê số lượng tiêu chí tìm thấy và chưa tìm thấy theo từng Ngân hàng & Năm
summary = df.groupby(["Bank", "Year"]).apply(
    lambda g: pd.Series({
        "Total_Indicators": len(g),
        "Found_Evidences": (g["Evidence"] != "NOT_FOUND_PUBLIC_EVIDENCE").sum(),
        "Not_Found_Evidences": (g["Evidence"] == "NOT_FOUND_PUBLIC_EVIDENCE").sum(),
        "Completion_Rate (%)": round(((g["Evidence"] != "NOT_FOUND_PUBLIC_EVIDENCE").sum() / len(g)) * 100, 2)
    })
).reset_index()

summary.to_csv("data_quality_raw.csv", index=False, encoding="utf-8-sig")
print("✅ Đã tạo xong file data_quality_raw.csv!")