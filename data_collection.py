import os
import re
import pandas as pd
import pdfplumber

# 1. Bảng ánh xạ 24 tiêu chí đầy đủ (Indicator ID -> Pillar, Indicator Name, Type)
INDICATORS_CONFIG = {
    "CUS1": {"pillar": "Customer Experience", "name": "eKYC & Số hóa mở account", "type": "Qualitative", "keywords": ["ekyc", "mở tài khoản online", "định danh điện tử", "xác thực khuôn mặt"]},
    "CUS2": {"pillar": "Customer Experience", "name": "Quy mô khách hàng số", "type": "Quantitative", "keywords": ["khách hàng số", "khách hàng active", "người dùng app", "active digital users"]},
    "CUS3": {"pillar": "Customer Experience", "name": "Tỷ lệ giao dịch số", "type": "Quantitative", "keywords": ["giao dịch số", "giao dịch kênh số", "tỷ lệ giao dịch", "kênh điện tử"]},
    "CUS4": {"pillar": "Customer Experience", "name": "Omnichannel & Cá nhân hóa", "type": "Qualitative", "keywords": ["omnichannel", "omni-channel", "trải nghiệm đa kênh", "cá nhân hóa"]},
    
    "STR1": {"pillar": "Strategy & Governance", "name": "Chiến lược & Lộ trình CĐS", "type": "Qualitative", "keywords": ["chiến lược số", "chiến lược chuyển đổi số", "roadmap", "digital strategy"]},
    "STR2": {"pillar": "Strategy & Governance", "name": "Cơ chế quản trị CĐS", "type": "Qualitative", "keywords": ["khối công nghệ", "trung tâm chuyển đổi số", "khối ngân hàng số", "ban công nghệ"]},
    "STR3": {"pillar": "Strategy & Governance", "name": "Đầu tư & Ngân sách IT", "type": "Qualitative", "keywords": ["ngân sách công nghệ", "đầu tư it", "chi phí phần mềm", "chi phí công nghệ"]},
    "STR4": {"pillar": "Strategy & Governance", "name": "Hợp tác hệ sinh thái", "type": "Qualitative", "keywords": ["hệ sinh thái", "đối tác fintech", "bigtech", "startup"]},
    
    "TEC1": {"pillar": "Technology & Infrastructure", "name": "Core Banking & Kiến trúc", "type": "Qualitative", "keywords": ["core banking", "microservices", "nâng cấp core"]},
    "TEC2": {"pillar": "Technology & Infrastructure", "name": "Cloud Computing", "type": "Qualitative", "keywords": ["cloud", "điện toán đám mây", "aws", "azure", "google cloud", "hybrid cloud"]},
    "TEC3": {"pillar": "Technology & Infrastructure", "name": "API & Open Banking", "type": "Qualitative", "keywords": ["open banking", "open api", "kết nối api", "baas"]},
    "TEC4": {"pillar": "Technology & Infrastructure", "name": "An toàn thông tin & Sinh trắc", "type": "Qualitative", "keywords": ["an toàn thông tin", "sinh trắc học", "soc", "chống gian lận", "bảo mật"]},
    "TEC5": {"pillar": "Technology & Infrastructure", "name": "AI & Machine Learning", "type": "Qualitative", "keywords": ["trí tuệ nhân tạo", "machine learning", "genai", "chatbot", "rpa", "ai"]},
    
    "OPS1": {"pillar": "Operations", "name": "End-to-end digital process", "type": "Qualitative", "keywords": ["online hoàn toàn", "quy trình số hóa", "end-to-end"]},
    "OPS2": {"pillar": "Operations", "name": "Tự động hóa & RPA", "type": "Qualitative", "keywords": ["tự động hóa", "rpa", "robot", "workflow"]},
    "OPS3": {"pillar": "Operations", "name": "Tín dụng số & STP", "type": "Qualitative", "keywords": ["digital lending", "phê duyệt tự động", "stp", "straight-through processing"]},
    "OPS4": {"pillar": "Operations", "name": "Paperless & Chữ ký số", "type": "Qualitative", "keywords": ["paperless", "chữ ký số", "e-signature", "hồ sơ điện tử"]},
    
    "CUL1": {"pillar": "Culture & Human Capital", "name": "Đào tạo năng lực số", "type": "Qualitative", "keywords": ["đào tạo kỹ năng số", "văn hóa số", "chương trình cđs nội bộ"]},
    "CUL2": {"pillar": "Culture & Human Capital", "name": "Đổi mới sáng tạo", "type": "Qualitative", "keywords": ["innovation lab", "hackathon", "sáng kiến đổi mới"]},
    "CUL3": {"pillar": "Culture & Human Capital", "name": "Agile & Ways of working", "type": "Qualitative", "keywords": ["agile", "scrum", "squad", "tribe", "cross-functional"]},
    "CUL4": {"pillar": "Culture & Human Capital", "name": "Nhân sự lãnh đạo công nghệ", "type": "Qualitative", "keywords": ["cdo", "cto", "cio", "nhân sự công nghệ", "tỷ trọng nhân sự it"]},
    
    "DAT1": {"pillar": "Data & Analytics", "name": "Nền tảng dữ liệu", "type": "Qualitative", "keywords": ["data lake", "data warehouse", "big data", "kho dữ liệu"]},
    "DAT2": {"pillar": "Data & Analytics", "name": "Data Governance & Bảo vệ DL", "type": "Qualitative", "keywords": ["data governance", "quản trị dữ liệu", "bảo vệ dữ liệu cá nhân"]},
    "DAT3": {"pillar": "Data & Analytics", "name": "Phân tích & Ứng dụng dữ liệu", "type": "Qualitative", "keywords": ["advanced analytics", "credit scoring", "fraud detection", "phân tích dữ liệu"]}
}

BANKS = ["ACB", "BIDV", "TCB", "VCB", "VPBank"]
YEARS = ["2021", "2022", "2023", "2024", "2025"]

def auto_generate_raw_data():
    # Load link nguồn từ source_catalog.csv nếu có
    catalog_links = {}
    if os.path.exists("source_catalog.csv"):
        try:
            cat_df = pd.read_csv("source_catalog.csv")
            for _, row in cat_df.iterrows():
                key = (str(row.get('Bank')).upper(), str(row.get('Year')))
                catalog_links[key] = row.get('Source_Link', '')
        except Exception:
            pass

    records = []
    print("🚀 Bắt đầu quét tự động & tạo file raw_data.csv...")

    for bank in BANKS:
        for year in YEARS:
            bank_year_dir = os.path.join("sources", bank, year)
            
            # Map kết quả tìm thấy cho từng tiêu chí
            found_evidences = {ind_id: None for ind_id in INDICATORS_CONFIG.keys()}

            if os.path.exists(bank_year_dir):
                for file in os.listdir(bank_year_dir):
                    if file.endswith(".pdf"):
                        file_path = os.path.join(bank_year_dir, file)
                        try:
                            with pdfplumber.open(file_path) as pdf:
                                for page_num, page in enumerate(pdf.pages, start=1):
                                    text = page.extract_text()
                                    if not text:
                                        continue

                                    for ind_id, cfg in INDICATORS_CONFIG.items():
                                        if found_evidences[ind_id] is not None:
                                            continue  # Đã tìm thấy bằng chứng tốt nhất trước đó thì bỏ qua

                                        for kw in cfg["keywords"]:
                                            if re.search(r'\b' + re.escape(kw) + r'\b', text, re.IGNORECASE):
                                                lines = text.split('\n')
                                                matching = [l.strip() for l in lines if re.search(r'\b' + re.escape(kw) + r'\b', l, re.IGNORECASE)]
                                                snippet = " | ".join(matching[:2])
                                                
                                                found_evidences[ind_id] = {
                                                    "Raw_Value": "Đã triển khai" if cfg["type"] == "Qualitative" else "Xem Evidence",
                                                    "Unit": "Văn bản" if cfg["type"] == "Qualitative" else "%",
                                                    "Evidence": snippet,
                                                    "Source_Name": file,
                                                    "Page": f"Trang {page_num}"
                                                }
                                                break
                        except Exception as e:
                            print(f"⚠️ Lỗi đọc file {file}: {e}")

            # Đưa thông tin vào bảng tổng hợp 13 cột
            source_link = catalog_links.get((bank.upper(), year), "")
            for ind_id, cfg in INDICATORS_CONFIG.items():
                res = found_evidences[ind_id]
                if res:
                    records.append({
                        "Bank": bank,
                        "Year": year,
                        "Indicator_ID": ind_id,
                        "Pillar": cfg["pillar"],
                        "Indicator": cfg["name"],
                        "Raw_Value": res["Raw_Value"],
                        "Unit": res["Unit"],
                        "Evidence": res["Evidence"],
                        "Source_Name": res["Source_Name"],
                        "Page/Section": res["Page"],
                        "Source_Link": source_link,
                        "Data_Type": cfg["type"],
                        "Note": "Auto-extracted"
                    })
                else:
                    # Điền trạng thái NOT_FOUND chuẩn quy định khi không thấy bằng chứng public
                    records.append({
                        "Bank": bank,
                        "Year": year,
                        "Indicator_ID": ind_id,
                        "Pillar": cfg["pillar"],
                        "Indicator": cfg["name"],
                        "Raw_Value": "NOT_FOUND_PUBLIC_EVIDENCE",
                        "Unit": "N/A",
                        "Evidence": "NOT_FOUND_PUBLIC_EVIDENCE",
                        "Source_Name": "N/A",
                        "Page/Section": "N/A",
                        "Source_Link": source_link,
                        "Data_Type": cfg["type"],
                        "Note": "NOT_FOUND_PUBLIC_EVIDENCE"
                    })

    df_out = pd.DataFrame(records)
    df_out.to_csv("raw_data.csv", index=False, encoding="utf-8-sig")
    print("✅ ĐÃ HOÀN THÀNH! File 'raw_data.csv' đã được tự động tạo xong đủ 600 dòng quan sát.")

if __name__ == "__main__":
    auto_generate_raw_data()