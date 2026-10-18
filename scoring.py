from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


BASE_DIR = Path(__file__).resolve().parent
RAW_FILE = BASE_DIR / "raw_data.csv"

BANK_ORDER = ["ACB", "BIDV", "TCB", "VCB", "VPBank"]
YEAR_ORDER = [2021, 2022, 2023, 2024, 2025]
PILLAR_ORDER = [
    "Customer Experience",
    "Strategy & Governance",
    "Technology & Infrastructure",
    "Operations",
    "Culture & Human Capital",
    "Data & Analytics",
]
QUANT_INDICATORS = {"CUS2", "CUS3"}

# Framework: an indicator missing for >= 3 banks in the same year is not used
# that year, so at least (n_banks - 2) banks must report a value.
MAX_MISSING_BANKS_PER_YEAR = 2

# Evidence present but no tier keyword found: rubric level 3 = "implemented,
# clear evidence" (level 2 is reserved for pilot / very limited scope).
DEFAULT_EVIDENCE_SCORE = 3.0

# Rubric tiers, checked from level 5 down to level 1 (first match wins).
QUALITATIVE_TIERS: list[tuple[float, list[str]]] = [
    (5.0, ["toàn diện", "toan dien", "quy mô lớn", "quy mo lon", "dẫn đầu", "100%", "cloud-first"]),
    (4.0, ["nhiều", "nhieu", "mở rộng", "mo rong", "rộng rãi", "phần lớn", "tích hợp sâu", "tiên tiến"]),
    (3.0, ["hoàn thành", "đã triển khai", "da trien khai", "vận hành", "van hanh", "áp dụng"]),
    (2.0, ["pilot", "thử nghiệm", "thuc nghiem", "trial", "phạm vi nhỏ", "đang ứng dụng"]),
    (1.0, ["kế hoạch", "ke hoach", "định hướng", "lộ trình", "dự kiến", "plan", "planned", "planning"]),
]


def _keyword_found(keyword: str, text: str) -> bool:
    """Whole-word/phrase match, so 'plan' does not fire on 'explanation'."""
    return re.search(rf"(?<!\w){re.escape(keyword)}(?!\w)", text) is not None


def is_missing(value: Any) -> bool:
    text = str(value).strip().lower()
    return text in {
        "",
        "nan",
        "none",
        "n/a",
        "na",
        "not_found_public_evidence",
    }


def normalize_text(value: Any) -> str:
    if is_missing(value):
        return ""
    return str(value).strip().lower()


def parse_number(value: Any) -> float:
    """Extract a numeric value from a raw CUS2/CUS3 field when available."""
    if is_missing(value):
        return np.nan
    text = str(value).replace(",", "").replace("%", " ")
    numbers = re.findall(r"[-+]?\d+(?:\.\d+)?", text)
    if not numbers:
        return np.nan
    try:
        return float(numbers[0])
    except ValueError:
        return np.nan


def qualitative_score(row: pd.Series) -> tuple[float | None, str]:
    """Score one qualitative row from its Evidence text only (0-5 or N/A)."""
    evidence = normalize_text(row.get("Evidence", ""))
    
    # 1. Bỏ qua nếu không tìm thấy minh chứng công khai -> Trả về N/A (np.nan)
    if not evidence or "not_found_public_evidence" in evidence:
        return np.nan, "N/A: No public evidence found"

    # 2. Kiểm tra nếu có bằng chứng xác nhận CHƯA TRIỂN KHAI -> Gán 0.0
    zero_keywords = ["chưa triển khai", "không triển khai", "ngưng", "dừng", "chua trien khai"]
    if any(k in evidence for k in zero_keywords):
        return 0.0, "Score 0.0: Confirmed not implemented"

    # 3. Quét các mức từ 5.0 xuống 1.0 theo từ khóa Rubric A.1
    for tier_score, keywords in QUALITATIVE_TIERS:
        for keyword in keywords:
            if keyword in evidence:  # Dùng substring match đơn giản để không bỏ sót từ
                return tier_score, f"Keyword tier {tier_score:g}: {keyword}"

    # 4. Có minh chứng hợp lệ nhưng không dính từ khóa đặc biệt -> Mức 2.0 (Bước đầu)
    return 2.0, "Evidence found, default tier 2.0"


def min_max_score(series: pd.Series) -> pd.Series:
    numeric = pd.to_numeric(series, errors="coerce")
    if numeric.notna().sum() == 0:
        return pd.Series(np.nan, index=series.index, dtype=float)
    minimum = numeric.min()
    maximum = numeric.max()
    if minimum == maximum:
        return pd.Series(2.5, index=series.index, dtype=float).where(numeric.notna())
    return 5 * (numeric - minimum) / (maximum - minimum)


def build_scored_data(raw: pd.DataFrame) -> pd.DataFrame:
    required = {"Bank", "Year", "Indicator_ID", "Pillar", "Indicator", "Raw_Value", "Evidence", "Data_Type"}
    missing_columns = required.difference(raw.columns)
    if missing_columns:
        raise ValueError(f"raw_data.csv missing columns: {sorted(missing_columns)}")

    cleaned = raw.copy()
    cleaned["Year"] = pd.to_numeric(cleaned["Year"], errors="coerce").astype("Int64")
    cleaned["Evidence_Missing"] = cleaned["Evidence"].map(is_missing)
    cleaned["Raw_Value_Missing"] = cleaned["Raw_Value"].map(is_missing)
    cleaned["Numeric_Value"] = np.nan
    cleaned["Score_0_5"] = np.nan
    cleaned["Scoring_Basis"] = ""

    for idx, row in cleaned.iterrows():
        indicator = str(row["Indicator_ID"]).strip()
        if indicator in QUANT_INDICATORS:
            cleaned.at[idx, "Numeric_Value"] = parse_number(row["Raw_Value"])
        else:
            score, basis = qualitative_score(row)
            cleaned.at[idx, "Score_0_5"] = score
            cleaned.at[idx, "Scoring_Basis"] = basis

    n_banks = int(cleaned["Bank"].nunique())
    min_available = max(1, n_banks - MAX_MISSING_BANKS_PER_YEAR)
    for indicator in sorted(QUANT_INDICATORS):
        mask = cleaned["Indicator_ID"].astype(str).str.strip().eq(indicator)
        sub = cleaned[mask]
        n_by_year = sub.groupby("Year")["Numeric_Value"].apply(lambda s: int(s.notna().sum()))
        usable_years = set(n_by_year[n_by_year >= min_available].index)
        usable = mask & cleaned["Year"].isin(usable_years)
        # default: not scoreable, with the reason written per row
        cleaned.loc[mask, "Score_0_5"] = np.nan
        for year, n in n_by_year.items():
            ymask = mask & cleaned["Year"].eq(year)
            if year in usable_years:
                cleaned.loc[ymask, "Scoring_Basis"] = "N/A: no numeric value for this bank"
            else:
                cleaned.loc[ymask, "Scoring_Basis"] = (
                    f"N/A: only {n}/{n_banks} banks report this in {year} "
                    f"(need >= {min_available}); indicator not used this year"
                )
        if usable.any():
            scores = min_max_score(cleaned.loc[usable, "Numeric_Value"])
            cleaned.loc[usable, "Score_0_5"] = scores
            has_val = usable & cleaned["Numeric_Value"].notna()
            cleaned.loc[has_val, "Scoring_Basis"] = "Min-Max across observations with a value"

    cleaned["Score_0_5"] = pd.to_numeric(cleaned["Score_0_5"], errors="coerce").round(4)
    return cleaned


def build_final_scores(scored: pd.DataFrame) -> pd.DataFrame:
    pillar = (
        scored.groupby(["Bank", "Year", "Pillar"], dropna=False)["Score_0_5"]
        .mean()
        .reset_index()
    )
    final = pillar.pivot_table(index=["Bank", "Year"], columns="Pillar", values="Score_0_5")
    final = final.reindex(columns=PILLAR_ORDER)
    final["Digital_Score"] = final[PILLAR_ORDER].mean(axis=1, skipna=True).round(4)
    final["Pillars_Available"] = final[PILLAR_ORDER].notna().sum(axis=1)
    final = final.reset_index()
    final["Rank"] = final.groupby("Year")["Digital_Score"].rank(method="min", ascending=False, na_option="keep").astype("Int64")
    return final.sort_values(["Year", "Rank", "Bank"]).reset_index(drop=True)


def build_quality(scored: pd.DataFrame) -> pd.DataFrame:
    quality = scored.groupby(["Bank", "Year"], dropna=False).agg(
        Total_Indicators=("Indicator_ID", "size"),
        Evidence_Found=("Evidence_Missing", lambda s: int((~s).sum())),
        Evidence_Missing=("Evidence_Missing", "sum"),
        Scoreable_Indicators=("Score_0_5", lambda s: int(s.notna().sum())),
        Nonscoreable_Indicators=("Score_0_5", lambda s: int(s.isna().sum())),
    ).reset_index()
    quality["Evidence_Coverage_Pct"] = (quality["Evidence_Found"] / quality["Total_Indicators"] * 100).round(2)
    quality["Score_Completion_Pct"] = (quality["Scoreable_Indicators"] / quality["Total_Indicators"] * 100).round(2)
    return quality


def build_sensitivity(scored: pd.DataFrame, full: pd.DataFrame) -> pd.DataFrame:
    reduced = scored[~scored["Indicator_ID"].isin(QUANT_INDICATORS)]
    pillar = reduced.groupby(["Bank", "Year", "Pillar"])["Score_0_5"].mean().reset_index()
    reduced_final = pillar.pivot_table(index=["Bank", "Year"], columns="Pillar", values="Score_0_5").reindex(columns=PILLAR_ORDER)
    reduced_final["Digital_Score_Without_CUS2_CUS3"] = reduced_final[PILLAR_ORDER].mean(axis=1, skipna=True)
    reduced_final = reduced_final[["Digital_Score_Without_CUS2_CUS3"]].reset_index()
    reduced_final["Rank_Without_CUS2_CUS3"] = reduced_final.groupby("Year")["Digital_Score_Without_CUS2_CUS3"].rank(method="min", ascending=False, na_option="keep").astype("Int64")
    result = full[["Bank", "Year", "Digital_Score", "Rank"]].merge(reduced_final, on=["Bank", "Year"], how="left")
    result["Rank_Changed"] = result["Rank"].ne(result["Rank_Without_CUS2_CUS3"])
    return result.sort_values(["Year", "Rank", "Bank"]).reset_index(drop=True)


def main() -> None:
    raw = pd.read_csv(RAW_FILE, encoding="utf-8-sig")
    scored = build_scored_data(raw)
    final = build_final_scores(scored)
    quality = build_quality(scored)
    sensitivity = build_sensitivity(scored, final)

    scored.to_csv(BASE_DIR / "scored_data.csv", index=False, encoding="utf-8-sig")
    scored.to_csv(BASE_DIR / "cleaned_data.csv", index=False, encoding="utf-8-sig")
    final.to_csv(BASE_DIR / "final_scores.csv", index=False, encoding="utf-8-sig")
    quality.to_csv(BASE_DIR / "data_quality.csv", index=False, encoding="utf-8-sig")
    sensitivity.to_csv(BASE_DIR / "sensitivity_check.csv", index=False, encoding="utf-8-sig")

    print(f"Scored indicators: {len(scored)}")
    print(f"Final bank-year rows: {len(final)}")
    print("Outputs written successfully.")


if __name__ == "__main__":
    main()