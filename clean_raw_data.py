import pandas as pd
import re

# Đọc trực tiếp file raw_data.csv
df = pd.read_csv('raw_data.csv')

# Danh sách từ khóa nhiễu địa chỉ và giao dịch cổ phiếu
noise_keywords = [
    'Láng Hạ', 'Đinh Bộ Lĩnh', 'Sở giao dịch', 'cổ phiếu', 
    'Địa chỉ', '024.', '028.', '0273.', 'TT Tên tổ chức', 'Khối lượng cổ phiếu'
]

count_cleaned = 0

for idx, row in df.iterrows():
    evidence = str(row['Evidence'])
    raw_val = str(row['Raw_Value'])
    indicator = str(row['Indicator_ID'])
    
    # 1. Lọc sạch từ khóa nhiễu ở cột Evidence
    if any(k in evidence for k in noise_keywords):
        df.at[idx, 'Evidence'] = 'NOT_FOUND_PUBLIC_EVIDENCE'
        df.at[idx, 'Raw_Value'] = 'NOT_FOUND_PUBLIC_EVIDENCE'
        count_cleaned += 1
        continue

    # 2. Xử lý trích xuất số cho CUS2 và CUS3
    if indicator in ['CUS2', 'CUS3'] and raw_val == 'Xem Evidence':
        match_pct = re.search(r'(\d+(?:[\.,]\d+)?\s*%)', evidence)
        match_num = re.search(r'(\d+(?:[\.,]\d+)?\s*(?:triệu|nghìn)\s*(?:KH|khách hàng)?)', evidence, re.IGNORECASE)
        
        if match_pct:
            df.at[idx, 'Raw_Value'] = match_pct.group(1)
        elif match_num:
            df.at[idx, 'Raw_Value'] = match_num.group(1)
        else:
            # Nếu Evidence không có con số cụ thể, gán NOT_FOUND_PUBLIC_EVIDENCE
            df.at[idx, 'Raw_Value'] = 'NOT_FOUND_PUBLIC_EVIDENCE'
            df.at[idx, 'Evidence'] = 'NOT_FOUND_PUBLIC_EVIDENCE'
        count_cleaned += 1

# Ghi đè lại file raw_data.csv
df.to_csv('raw_data.csv', index=False)
print(f"✅ Đã tự động xử lý và làm sạch {count_cleaned} dòng trong raw_data.csv!")