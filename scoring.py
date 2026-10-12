"""Clean, score, rank and quality-check DigitalBank raw evidence.

Input:  raw_data.csv (600 rows: 5 banks x 5 years x 24 indicators)
Outputs:
  cleaned_data.csv   normalized raw values and missing-data flags
  scored_data.csv    indicator-level scores on a 0-5 scale
  final_scores.csv   pillar scores, Digital Score and yearly rank
  data_quality.csv   coverage and missingness by bank-year
  sensitivity_check.csv  full ranking vs ranking without CUS2/CUS3

This is a transparent, public-data-based index. A missing public citation is
scored as 0 for qualitative indicators, but the output keeps the missing flag;
that score does not mean the bank definitely lacks the capability.
"""
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

# Conservative qualitative anchors. The rule is deliberately explicit and
# reproducible; project members can revise this table after evidence review.
QUALITATIVE_ANCHORS = {
    "plan": 1,
    "planned": 1,
    "pilot": 2,
    "thử nghiệm": 2,
    "thuc nghiem": 2,
    "trial": 2,
    "đã triển khai": 3,
    "da trien khai": 3,
    "triển khai": 3,
    "trien khai": 3,
    "vận hành": 3,
    "van hanh": 3,
    "nhiều": 4,
    "nhieu": 4,
    "toàn diện": 5,
    "toan dien": 5,
    "quy mô lớn": 5,
    "quy mo lon": 5,
}


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


def qualitative_score(row: pd.Series) -> tuple[float, str]:
    evidence = normalize_text(row.get("Evidence", ""))
    raw_value = normalize_text(row.get("Raw_Value", ""))
    if not evidence or "not_found_public_evidence" in evidence:
        return 0.0, "No public evidence found; score 0 per rubric"

    combined = f"{raw_value} {evidence}"
    score = 3
    basis = "Evidence found; conservative implemented score 3"
    for anchor, anchor_score in sorted(QUALITATIVE_ANCHORS.items(), key=lambda item: len(item[0]), reverse=True):
        if anchor in combined:
            score = max(score, anchor_score)
            basis = f"Keyword anchor: {anchor}"
            break
    return float(min(score, 5)), basis


def min_max_score(series: pd.Series) -> pd.Series:
    numeric = pd.to_numeric(series, errors="coerce")
    if numeric.notna().sum() == 0:
        return pd.Series(np.nan, index=series.index, dtype=float)
    minimum = numeric.min()
    maximum = numeric.max()
    if minimum == maximum:
        return pd.Series(2.5, index=series.index, dtype=float)
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
            cleaned.at[idx, "Scoring_Basis"] = "Min-Max across all 25 bank-year observations"
        else:
            score, basis = qualitative_score(row)
            cleaned.at[idx, "Score_0_5"] = score
            cleaned.at[idx, "Scoring_Basis"] = basis

    for indicator in QUANT_INDICATORS:
        mask = cleaned["Indicator_ID"].eq(indicator)
        cleaned.loc[mask, "Score_0_5"] = min_max_score(cleaned.loc[mask, "Numeric_Value"])

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
