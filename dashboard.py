import os
import re
import unicodedata

import dash
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from dash import Input, Output, dash_table, dcc, html

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ==========================================================
# 1. HẰNG SỐ GIAO DIỆN & NẠP DỮ LIỆU
# ==========================================================
PILLARS = ["Customer", "Strategy", "Technology", "Operations", "Culture", "Data"]
PILLAR_VN = {
    "Customer": "Khách hàng", "Strategy": "Chiến lược", "Technology": "Công nghệ",
    "Operations": "Vận hành", "Culture": "Văn hóa", "Data": "Dữ liệu",
}
PILLAR_PREFIX = {
    "CUS": "Customer", "STR": "Strategy", "TEC": "Technology",
    "OPS": "Operations", "CUL": "Culture", "DAT": "Data",
}
PILLAR_ORDER = {p: i for i, p in enumerate(PILLARS)}
QUANT_IDS = ["CUS2", "CUS3"]  # 2 chỉ tiêu định lượng dùng cho sensitivity check

BANK_NAMES = {"TCB": "Techcombank", "BIDV": "BIDV", "VCB": "Vietcombank",
              "VPB": "VPBank", "ACB": "ACB"}
BANK_COLORS = {"TCB": "#FF4D6D", "BIDV": "#4F46E5", "VCB": "#10B981",
               "VPB": "#F59E0B", "ACB": "#06B6D4"}
ATM_BACKGROUNDS = {
    "TCB": "linear-gradient(135deg,#FF4D6D 0%,#F472B6 48%,#8B5CF6 100%)",
    "BIDV": "linear-gradient(135deg,#4F46E5 0%,#8B5CF6 50%,#F472B6 100%)",
    "VCB": "linear-gradient(135deg,#10B981 0%,#2DD4BF 45%,#A78BFA 100%)",
    "VPB": "linear-gradient(135deg,#F59E0B 0%,#FB7185 50%,#A855F7 100%)",
    "ACB": "linear-gradient(135deg,#06B6D4 0%,#818CF8 50%,#F472B6 100%)",
}
DEFAULT_ATM_BG = "linear-gradient(135deg,#8B5CF6 0%,#C084FC 50%,#F472B6 100%)"
PILLAR_COLORS = {"Customer": "#7C3AED", "Strategy": "#C084FC", "Technology": "#F472B6",
                 "Operations": "#FDBA74", "Culture": "#2DD4BF", "Data": "#312E81"}
HEAT_SCALE = [[0.0, "#FFF4FA"], [0.2, "#F9CDE8"], [0.5, "#D883E8"],
              [0.75, "#9B5CF0"], [1.0, "#4C1D95"]]
FONT = "'Plus Jakarta Sans', 'Be Vietnam Pro', 'Segoe UI', Roboto, Helvetica, Arial, sans-serif"
INK, MUTED = "#2A1F57", "#6B5F92"
GRID = "rgba(139,92,246,0.12)"
HEAT_SCALE_DARK = [[0.0, "#2A2250"], [0.2, "#4B2A7A"], [0.5, "#8B3FBF"],
                   [0.75, "#D05CD8"], [1.0, "#FF9BE0"]]


def theme(dark):
    """Bảng màu cho biểu đồ Plotly (Plotly không đọc được biến CSS)."""
    if dark:
        return dict(ink="#EDE7FF", muted="#B7ABDA", grid="rgba(190,170,255,0.16)",
                    polar="rgba(255,255,255,0.04)", pie_edge="#272A52", avg="#B7ABDA",
                    heat=HEAT_SCALE_DARK, na_bg="rgba(190,170,255,0.10)", na_text="#8E83B8",
                    card="#272A52", na_slice="#5A5688", note_bg="rgba(39,42,82,0.9)")
    return dict(ink=INK, muted=MUTED, grid=GRID, polar="rgba(250,240,252,0.7)", pie_edge="white",
                avg="#6B5F92", heat=HEAT_SCALE, na_bg="rgba(139,92,246,0.10)", na_text="#8A7FB0",
                card="white", na_slice="#D9D2EC", note_bg="rgba(255,255,255,0.8)")


def _read_csv(name, required=True):
    path = os.path.join(BASE_DIR, name)
    if not os.path.exists(path):
        if required:
            raise FileNotFoundError(f"Không tìm thấy {name} trong {BASE_DIR}")
        return pd.DataFrame()
    return pd.read_csv(path)

def _clean_keys(df):
    df = df.copy()
    # Cắt sạch khoảng trắng thừa và ép chữ hoa cho Bank
    df["Bank"] = df["Bank"].astype(str).str.strip().str.upper()
    df["Year"] = pd.to_numeric(df["Year"], errors="coerce")
    df = df.dropna(subset=["Year"])
    df["Year"] = df["Year"].astype(int)
    return df

def _norm(text):
    """Bỏ dấu tiếng Việt, ký tự đặc biệt, chữ hoa -> so khớp tên cột linh hoạt."""
    t = unicodedata.normalize("NFKD", str(text).replace("đ", "d").replace("Đ", "D"))
    t = "".join(ch for ch in t if not unicodedata.combining(ch))
    return re.sub(r"[^a-z0-9]", "", t.lower())

def load_all_data():
    """Hàm nạp lại dữ liệu CSV trực tiếp từ đĩa để tránh dính Cache cũ."""
    final_full = _clean_keys(_read_csv("final_scores.csv"))
    scored = _clean_keys(_read_csv("scored_data.csv"))
    raw = _clean_keys(_read_csv("raw_data.csv"))
    dq_df = _read_csv("data_quality.csv", required=False)

    # Đảm bảo ép sạch Indicator_ID không dính khoảng trắng
    scored["Indicator_ID"] = scored["Indicator_ID"].astype(str).str.strip().str.upper()
    scored["Score_0_5"] = pd.to_numeric(scored["Score_0_5"], errors="coerce")
    scored["PillarKey"] = scored["Indicator_ID"].str[:3].map(PILLAR_PREFIX)

    raw["Indicator_ID"] = raw["Indicator_ID"].astype(str).str.strip().str.upper()
    raw["PillarKey"] = raw["Indicator_ID"].str[:3].map(PILLAR_PREFIX)

    return final_full, scored, raw, dq_df

# Kích hoạt nạp dữ liệu
final_full, scored, raw, dq_df = load_all_data()

# --- Nhận diện tên cột trụ cột trong final_scores.csv ---
PILLAR_ALIASES = {
    "Customer": ("customer", "cus", "khachhang"),
    "Strategy": ("strategy", "str", "chienluoc"),
    "Technology": ("technology", "tech", "tec", "congnghe"),
    "Operations": ("operations", "operation", "ops", "vanhanh"),
    "Culture": ("culture", "cul", "vanhoa"),
    "Data": ("data", "dat", "dulieu"),
}
_META_COLS = {"bank", "year", "digitalscore", "rank", "pillarsavailable", "rankfull"}
print("[INFO] Cột trong final_scores.csv:", list(final_full.columns))
final_full.columns = [str(c).strip() for c in final_full.columns]
_rename = {}
for _p, _aliases in PILLAR_ALIASES.items():
    if _p in final_full.columns:
        continue
    for _c in final_full.columns:
        _n = _norm(_c)
        if _n in _META_COLS or _c in PILLARS or _c in _rename:
            continue
        if any(_n.startswith(a) for a in _aliases):
            _rename[_c] = _p
            break
final_full = final_full.rename(columns=_rename)
if _rename:
    print("[INFO] Đã đổi tên cột trụ cột:", _rename)
for _p in PILLARS:
    if _p not in final_full.columns:
        final_full[_p] = np.nan
    else:
        final_full[_p] = pd.to_numeric(final_full[_p], errors="coerce")


def _all_pillars_mean(df):
    """Digital Score = TB 6 trụ cột; thiếu bất kỳ trụ cột nào -> N/A (khớp scoring.py)."""
    return df[PILLARS].mean(axis=1).where(df[PILLARS].notna().all(axis=1))


if "Digital_Score" not in final_full.columns:
    final_full["Digital_Score"] = _all_pillars_mean(final_full)
final_full["Digital_Score"] = pd.to_numeric(final_full["Digital_Score"], errors="coerce")

# Sửa lại cách tạo Dict Tên chỉ tiêu: loại bỏ khoảng trắng và dòng trống
if "Indicator" in scored.columns:
    _valid_ind = scored.dropna(subset=["Indicator"]).copy()
    _valid_ind["Indicator_ID"] = _valid_ind["Indicator_ID"].astype(str).str.strip().str.upper()
    INDICATOR_NAME = _valid_ind.drop_duplicates("Indicator_ID").set_index("Indicator_ID")["Indicator"].to_dict()
else:
    INDICATOR_NAME = {}


def _indicator_sort_key(ind_id):
    pillar = PILLAR_PREFIX.get(str(ind_id)[:3], "")
    num = re.sub(r"\D", "", str(ind_id)) or "0"
    return (PILLAR_ORDER.get(pillar, 99), int(num))


def compute_final(drop_ids=()):
    """Tính lại điểm trụ cột / Digital Score / Rank từ scored_data.csv,
    bỏ các Indicator_ID trong drop_ids (kịch bản sensitivity)."""
    d = scored[~scored["Indicator_ID"].isin(drop_ids)].dropna(subset=["PillarKey"])
    piv = d.groupby(["Bank", "Year", "PillarKey"])["Score_0_5"].mean().unstack("PillarKey")
    for p in PILLARS:
        if p not in piv.columns:
            piv[p] = np.nan
    piv = piv[PILLARS]
    piv["Digital_Score"] = _all_pillars_mean(piv)   # thiếu 1 trụ cột -> N/A, giống scoring.py
    out = piv.reset_index()
    out["Rank"] = out.groupby("Year")["Digital_Score"].rank(method="min", ascending=False)  # N/A giữ NaN
    return out


# Bổ sung trụ cột thiếu từ scored_data.csv (nếu final_scores.csv không đủ)
_re = compute_final(())
_fill = final_full[["Bank", "Year"]].merge(_re[["Bank", "Year"] + PILLARS], on=["Bank", "Year"], how="left")
for _p in PILLARS:
    _vals = pd.Series(_fill[_p].values, index=final_full.index)
    _before = int(final_full[_p].isna().sum())
    final_full[_p] = final_full[_p].fillna(_vals)
    _filled = _before - int(final_full[_p].isna().sum())
    if _filled:
        print(f"[CẢNH BÁO] Trụ cột {_p}: bổ sung {_filled} ô từ scored_data.csv")

# Bank-year thiếu hẳn một trụ cột (không có bằng chứng nào chấm được) -> Digital_Score/Rank = N/A.
# Các view xếp hạng chỉ dùng bank-year có điểm; phần còn lại được ghi chú là "chưa xếp hạng".
final_full["Digital_Score"] = final_full["Digital_Score"].fillna(_all_pillars_mean(final_full))
ALL_BANKS = sorted(final_full["Bank"].unique().tolist())
final_full = final_full[final_full["Digital_Score"].notna()].copy()
final_full["Rank"] = final_full.groupby("Year")["Digital_Score"].rank(method="min", ascending=False).astype(int)
final_full["Rank_Full"] = final_full["Rank"]

final_sens = (compute_final(QUANT_IDS).dropna(subset=["Digital_Score"])
              .merge(final_full[["Bank", "Year", "Rank_Full"]], on=["Bank", "Year"], how="left"))
final_sens["Rank"] = final_sens["Rank"].astype(int)
final_sens["Rank_Full"] = final_sens["Rank_Full"].fillna(final_sens["Rank"]).astype(int)
SCENARIOS = {False: final_full, True: final_sens}


def get_scores(sens):
    return SCENARIOS[bool(sens)]


# Kịch bản bỏ CUS2/CUS3 có khác kịch bản đầy đủ không?
_cmp = final_full.merge(final_sens, on=["Bank", "Year"], suffixes=("", "_s"))
SENS_IDENTICAL = bool(len(_cmp) and (_cmp["Digital_Score"] - _cmp["Digital_Score_s"]).abs().max() < 1e-3)  # CSV làm tròn 4 chữ số


def check_consistency():
    m = final_full.merge(compute_final(()), on=["Bank", "Year"], suffixes=("", "_re"))
    if m.empty:
        print("[CẢNH BÁO] Không đối chiếu được final_scores.csv với scored_data.csv")
        return
    diff = (m["Digital_Score"] - m["Digital_Score_re"]).abs().max()
    rank_bad = int((m["Rank"] != m["Rank_re"]).sum())
    if diff > 0.01 or rank_bad:
        print(f"[CẢNH BÁO] Lệch final_scores.csv vs scored_data.csv: max|ΔDigital_Score|={diff:.3f}, "
              f"số dòng lệch Rank={rank_bad}.")
    else:
        print("[OK] final_scores.csv khớp với scored_data.csv.")


check_consistency()

YEARS = sorted(final_full["Year"].unique().tolist(), reverse=True)
LATEST, FIRST = YEARS[0], YEARS[-1]
BANKS = final_full[final_full["Year"] == LATEST].sort_values("Rank")["Bank"].tolist()

# --- Bảng bằng chứng: raw_data + điểm từ scored_data ---
_score_cols = scored[["Bank", "Year", "Indicator_ID", "Score_0_5"]].drop_duplicates(
    ["Bank", "Year", "Indicator_ID"])
EVID = raw.merge(_score_cols, on=["Bank", "Year", "Indicator_ID"], how="left")
_nf_cols = [c for c in ["Raw_Value", "Note", "Evidence"] if c in EVID.columns]
_not_found = (EVID[_nf_cols].astype(str).apply(lambda s: s.str.upper().str.contains("NOT_FOUND"))
              .any(axis=1))
_has_evid = (EVID["Evidence"].notna() & (EVID["Evidence"].astype(str).str.strip() != "")
             if "Evidence" in EVID.columns else pd.Series(False, index=EVID.index))
EVID["Is_Valid_Evidence"] = (~_not_found) & _has_evid
_search_cols = [c for c in ["Indicator_ID", "Indicator", "Raw_Value", "Evidence", "Note", "Source_Name"]
                if c in EVID.columns]
EVID["_search"] = EVID[_search_cols].fillna("").astype(str).agg(" ".join, axis=1).str.lower()
EVID_SHOW_COLS = [c for c in ["Bank", "Year", "Indicator_ID", "Indicator", "Raw_Value", "Score_0_5",
                              "Evidence", "Source_Name", "Page/Section", "Source_Link"]
                  if c in EVID.columns]
EVID_HEADER = {"Score_0_5": "Điểm (0–5)", "Indicator_ID": "Mã", "Raw_Value": "Raw Value",
               "Page/Section": "Trang/Mục", "Source_Name": "Nguồn", "Source_Link": "Liên kết"}

# ==========================================================
# 2. TIỆN ÍCH & BIỂU ĐỒ
# ==========================================================
GRAPH_CONFIG = {"displaylogo": False, "toImageButtonOptions": {"format": "png", "scale": 2}}


def hex_to_rgba(hex_color, alpha):
    h = hex_color.lstrip("#")
    r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
    return f"rgba({r},{g},{b},{alpha})"


def base_layout(dark=False, **kwargs):
    t = theme(dark)
    layout = dict(
        font=dict(family=FONT, size=13, color=t["ink"]),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=30, r=30, t=60, b=30),
        legend=dict(orientation="h", y=-0.15, x=0.5, xanchor="center"),
        hoverlabel=dict(bgcolor=t["card"], font=dict(family=FONT, color=t["ink"])),
    )
    layout.update(kwargs)
    return layout


def title_dict(text, dark=False):
    return dict(text=text, x=0.02, font=dict(size=16, family=FONT, color=theme(dark)["ink"]))


def fig_trend(sens, dark=False):
    t = theme(dark)
    df = get_scores(sens)
    fig = go.Figure()
    for bank in BANKS:
        d = df[df["Bank"] == bank].set_index("Year").reindex(sorted(YEARS)).reset_index()
        fig.add_trace(go.Scatter(
            x=d["Year"], y=d["Digital_Score"], mode="lines+markers", name=bank, connectgaps=False,
            line=dict(width=3, color=BANK_COLORS.get(bank, "#8B5CF6"), shape="spline", smoothing=0.5),
            marker=dict(size=9, line=dict(width=2, color=t["card"])), hovertemplate="%{y:.2f}"))
    avg = df.groupby("Year")["Digital_Score"].mean().sort_index()
    fig.add_trace(go.Scatter(x=avg.index, y=avg.values, mode="lines", name="TB các NH có điểm",
                             line=dict(width=2.5, color=t["avg"], dash="dash"), hovertemplate="%{y:.2f}"))
    lo, hi = df["Digital_Score"].min(), df["Digital_Score"].max()
    fig.update_layout(**base_layout(
        dark, title=title_dict("Digital Score 2021–2025 (năm thiếu bằng chứng ở một trụ cột: N/A, không vẽ)", dark),
        xaxis=dict(tickmode="linear", dtick=1, gridcolor=t["grid"]),
        yaxis=dict(title="Digital Score (0–5)", gridcolor=t["grid"],
                   range=[max(0, lo - 0.3), min(5, hi + 0.3)]),
        hovermode="x unified", height=430))
    return fig


def fig_radar(year, banks, sens, title=None, dark=False):
    t = theme(dark)
    df = get_scores(sens)
    d = df[(df["Year"] == year) & (df["Bank"].isin(banks or []))]
    fig = go.Figure()
    theta = [PILLAR_VN[p] for p in PILLARS]
    for bank in [b for b in BANKS if b in set(d["Bank"])]:
        row = d[d["Bank"] == bank].iloc[0]
        vals = [row[p] for p in PILLARS]
        color = BANK_COLORS.get(bank, "#8B5CF6")
        fig.add_trace(go.Scatterpolar(
            r=vals + vals[:1], theta=theta + theta[:1], name=bank, fill="toself",
            fillcolor=hex_to_rgba(color, 0.22 if dark else 0.16), line=dict(color=color, width=2.5),
            hovertemplate="%{theta}: %{r:.2f}<extra>" + bank + "</extra>"))
    fig.update_layout(**base_layout(
        dark, title=title_dict(title or f"Sáu trụ cột năm {year}", dark),
        polar=dict(bgcolor=t["polar"],
                   radialaxis=dict(visible=True, range=[0, 5], gridcolor=t["grid"], linecolor=t["grid"]),
                   angularaxis=dict(gridcolor=t["grid"], linecolor=t["grid"], tickfont=dict(size=13))),
        height=430))
    return fig


def fig_stacked(year, banks, sens, dark=False):
    """Cột = Digital Score; mỗi phân đoạn = điểm trụ cột ÷ 6 (tổng 6 phân đoạn = Digital Score)."""
    t = theme(dark)
    df = get_scores(sens)
    d = df[(df["Year"] == year) & (df["Bank"].isin(banks or []))].sort_values("Rank")
    fig = go.Figure()
    for p in PILLARS:
        fig.add_trace(go.Bar(
            x=d["Bank"], y=d[p] / 6, name=PILLAR_VN[p], marker_color=PILLAR_COLORS[p],
            customdata=d[p],
            hovertemplate="%{x} – " + PILLAR_VN[p] +
                          "<br>Điểm trụ cột: %{customdata:.2f}<br>Đóng góp: %{y:.2f}<extra></extra>"))
    fig.add_trace(go.Scatter(x=d["Bank"], y=d["Digital_Score"], mode="text",
                             text=[f"{v:.2f}" for v in d["Digital_Score"]], textposition="top center",
                             textfont=dict(size=14, color=t["ink"]), showlegend=False, hoverinfo="skip"))
    top = d["Digital_Score"].max() if len(d) else 5
    fig.update_layout(**base_layout(
        dark, title=title_dict(f"Cơ cấu đóng góp của 6 trụ cột năm {year}", dark), barmode="stack", height=430,
        yaxis=dict(title="Digital Score", range=[0, min(5.2, top + 0.5)], gridcolor=t["grid"])))
    return fig


def heat_frame(year, pillar, sens, hide_na):
    d = scored[scored["Year"] == year].copy()
    if sens:
        d = d[~d["Indicator_ID"].isin(QUANT_IDS)]
    if pillar and pillar != "ALL":
        d = d[d["PillarKey"] == pillar]
    if d.empty:
        return None, []
    pv = (d.drop_duplicates(["Bank", "Indicator_ID"])
          .pivot(index="Indicator_ID", columns="Bank", values="Score_0_5"))
    pv = pv.reindex(index=sorted(pv.index, key=_indicator_sort_key),
                    columns=[b for b in BANKS if b in pv.columns])
    all_na = [i for i in pv.index if pv.loc[i].isna().all()]
    if hide_na:
        pv = pv.drop(index=all_na)
    return pv, all_na


def fig_heatmap(year, pillar, sens, hide_na=False, dark=False):
    t = theme(dark)
    pv, _ = heat_frame(year, pillar, sens, hide_na)
    if pv is None or pv.empty:
        return go.Figure().update_layout(**base_layout(
            dark, title=title_dict("Chưa có dữ liệu", dark), height=300))
    ylabels = [f"{i} · {INDICATOR_NAME.get(i, '')}"[:46] for i in pv.index]
    z = pv.values
    fig = go.Figure(go.Heatmap(
        z=z, x=list(pv.columns), y=ylabels, zmin=0, zmax=5, xgap=3, ygap=3,
        colorscale=t["heat"], hoverongaps=False,
        colorbar=dict(title="Điểm", thickness=14, len=0.6, outlinewidth=0),
        hovertemplate="%{y}<br>%{x}: %{z:.1f}<extra></extra>"))
    for i in range(z.shape[0]):
        for j in range(z.shape[1]):
            v = z[i, j]
            if np.isnan(v):
                txt, col = "N/A", t["na_text"]
            else:
                txt = f"{v:.1f}"
                if dark:
                    col = "#1B1238" if v >= 4.5 else "#FFFFFF"
                else:
                    col = "white" if v >= 3 else t["ink"]
            fig.add_annotation(x=pv.columns[j], y=ylabels[i], showarrow=False, text=txt,
                               font=dict(size=12, color=col))
    n = len(pv.index)
    fig.update_layout(**base_layout(
        dark, title=title_dict(f"Ma trận {n} tiêu chí năm {year}", dark),
        plot_bgcolor=t["na_bg"],  # ô N/A hiện nền tím nhạt
        yaxis=dict(autorange="reversed", type="category", tickfont=dict(size=11)),
        xaxis=dict(type="category", side="top", tickfont=dict(size=13)),
        height=max(260, 34 * n + 120), margin=dict(l=30, r=30, t=90, b=20)))
    return fig


def heat_note(year, pillar, sens):
    pv, all_na = heat_frame(year, pillar, sens, False)
    parts = []
    if all_na:
        parts.append(f"{', '.join(all_na)} chưa có số liệu định lượng cùng định nghĩa cho cả "
                     f"{len(BANKS)} ngân hàng trong năm {year} (N/A), nên không được tính vào điểm trụ cột "
                     f"(xem data_quality.csv). Cần bổ sung dữ liệu gốc từ khâu thu thập.")
    if pv is not None and pv.isna().any().any():
        parts.append("Ô N/A: không tìm thấy bằng chứng công khai (hoặc thiếu số liệu so sánh), không phải điểm 0 "
                     "và không tính vào điểm trụ cột; không khẳng định ngân hàng không triển khai. "
                     "Điểm 0 chỉ khi bằng chứng xác nhận chưa/không triển khai. Điểm 1–5 theo mức độ triển khai "
                     "trong bằng chứng; bằng chứng không chứa từ khóa mức nào được chấm mặc định 2.")
    return " ".join(parts)


def fig_h2h_trend(a, b, sens, dark=False):
    t = theme(dark)
    df = get_scores(sens)
    fig = go.Figure()
    for bank in (a, b):
        d = df[df["Bank"] == bank].sort_values("Year")
        fig.add_trace(go.Scatter(
            x=d["Year"], y=d["Digital_Score"], mode="lines+markers+text", name=bank,
            text=[f"{v:.2f}" for v in d["Digital_Score"]], textposition="top center",
            line=dict(width=3, color=BANK_COLORS.get(bank, "#8B5CF6"), shape="spline", smoothing=0.5),
            marker=dict(size=9, line=dict(width=2, color=t["card"]))))
    fig.update_layout(**base_layout(
        dark, title=title_dict(f"{a} và {b}: Digital Score {FIRST}–{LATEST}", dark), height=430,
        xaxis=dict(tickmode="linear", dtick=1, gridcolor=t["grid"]),
        yaxis=dict(title="Digital Score", gridcolor=t["grid"]), hovermode="x unified"))
    return fig


# ---------- Bản đồ định vị & SWOT ----------
QUADRANTS = {
    "TR": "Dẫn đầu · tăng nhanh", "TL": "Bám đuổi · tăng nhanh",
    "BR": "Điểm cao · tăng chậm", "BL": "Cần tăng tốc",
}


def quadrant_of(x, y, xm, ym):
    return QUADRANTS[("T" if y >= ym else "B") + ("R" if x >= xm else "L")]


def _pos_all(year, sens):
    df = get_scores(sens)
    cur = df[df["Year"] == year].set_index("Bank")
    rows = {}
    for bank, r in cur.iterrows():
        prior = df[(df["Bank"] == bank) & (df["Year"] < year)].sort_values("Year")
        if prior.empty:
            rows[bank] = dict(x=r["Digital_Score"], y=np.nan, rank=r["Rank"], base=year)
        else:
            rows[bank] = dict(x=r["Digital_Score"], y=r["Digital_Score"] - prior.iloc[0]["Digital_Score"],
                              rank=r["Rank"], base=int(prior.iloc[0]["Year"]))
    cols = ["x", "y", "rank", "base"]
    return pd.DataFrame.from_dict(rows, orient="index", columns=cols) if rows else pd.DataFrame(columns=cols)


def pos_data(year, sens):
    """Chỉ gồm ngân hàng có điểm năm này VÀ có mốc so sánh (một năm trước đó có điểm)."""
    return _pos_all(year, sens).dropna(subset=["x", "y"])


def pos_nobase(year, sens):
    a = _pos_all(year, sens)
    return a[a["y"].isna()].index.tolist()


def fig_positioning(year, sens, dark=False):
    t = theme(dark)
    d = pos_data(year, sens)
    if d.empty:
        fig = go.Figure()
        fig.add_annotation(x=0.5, y=0.5, xref="paper", yref="paper", showarrow=False,
                           text="Chưa đủ dữ liệu để so sánh: cần ít nhất hai năm có Digital Score của cùng một ngân hàng.",
                           font=dict(size=13, color=t["muted"]), bgcolor=t["note_bg"])
        fig.update_layout(**base_layout(dark, title=title_dict(f"Bản đồ định vị năm {year}", dark), height=520))
        return fig
    xm, ym = d["x"].mean(), d["y"].mean()
    px_, py_ = max(0.25, (d["x"].max() - d["x"].min()) * 0.4), max(0.25, (d["y"].max() - d["y"].min()) * 0.4)
    x0, x1 = d["x"].min() - px_, d["x"].max() + px_
    y0, y1 = d["y"].min() - py_, d["y"].max() + py_
    fig = go.Figure()
    a = 0.16 if dark else 0.10
    for (xa, xb, ya, yb, col) in [(xm, x1, ym, y1, f"139,92,246,{a}"), (x0, xm, ym, y1, f"244,114,182,{a}"),
                                   (xm, x1, y0, ym, f"45,212,191,{a}"), (x0, xm, y0, ym, f"253,186,116,{a + 0.04}")]:
        fig.add_shape(type="rect", x0=xa, x1=xb, y0=ya, y1=yb, fillcolor=f"rgba({col})",
                      line=dict(width=0), layer="below")
    for bank, r in d.iterrows():
        fig.add_trace(go.Scatter(
            x=[r["x"]], y=[r["y"]], mode="markers+text", text=[bank], textposition="top center",
            textfont=dict(size=14, color=t["ink"]), name=bank, showlegend=False,
            marker=dict(size=34, color=BANK_COLORS.get(bank, "#8B5CF6"), line=dict(width=3, color=t["card"])),
            hovertemplate=f"<b>{bank}</b><br>Digital Score: {r['x']:.2f}<br>"
                          f"Thay đổi so với {int(r['base'])}: {r['y']:+.2f}<br>Hạng: {int(r['rank'])}<extra></extra>"))
    fig.add_vline(x=xm, line_dash="dash", line_color=t["muted"], opacity=0.6)
    fig.add_hline(y=ym, line_dash="dash", line_color=t["muted"], opacity=0.6)
    for txt, x, y, xa, ya in [(QUADRANTS["TR"], x1, y1, "right", "top"), (QUADRANTS["TL"], x0, y1, "left", "top"),
                              (QUADRANTS["BR"], x1, y0, "right", "bottom"), (QUADRANTS["BL"], x0, y0, "left", "bottom")]:
        fig.add_annotation(x=x, y=y, text=txt, showarrow=False, xanchor=xa, yanchor=ya,
                           font=dict(size=12, color=t["muted"]))
    _nb = pos_nobase(year, sens)
    if _nb:
        fig.add_annotation(x=0.01, y=0.01, xref="paper", yref="paper", showarrow=False, xanchor="left",
                           yanchor="bottom", text=f"Chưa có mốc so sánh: {', '.join(_nb)}",
                           font=dict(size=12, color=t["muted"]), bgcolor=t["note_bg"])
    fig.update_layout(**base_layout(
        dark, title=title_dict(f"Bản đồ định vị năm {year}: vị thế và tốc độ cải thiện", dark), height=520,
        xaxis=dict(title=f"Digital Score năm {year}", range=[x0, x1], gridcolor=t["grid"], zeroline=False),
        yaxis=dict(title="Thay đổi điểm so với năm đầu có điểm của từng ngân hàng", range=[y0, y1], gridcolor=t["grid"], zeroline=False)))
    return fig


def build_swot(bank, year, sens):
    df = get_scores(sens)
    cur = df[df["Year"] == year].set_index("Bank")
    if bank not in cur.index:
        return None
    avg, row = cur[PILLARS].mean(), cur.loc[bank]
    S, W, O, T = [], [], [], []

    # Trụ cột so với TB nhóm
    pdelta = (row[PILLARS] - avg).dropna()
    for p, dl in pdelta.sort_values(ascending=False).items():
        if dl >= 0.05 and len(S) < 2:
            S.append(f"Trụ cột {PILLAR_VN[p]}: {row[p]:.2f} điểm, cao hơn TB nhóm {dl:+.2f}")
    for p, dl in pdelta.sort_values().items():
        if dl <= -0.05 and len(W) < 2:
            W.append(f"Trụ cột {PILLAR_VN[p]}: {row[p]:.2f} điểm, thấp hơn TB nhóm {dl:+.2f}")

    # Tiêu chí so với các ngân hàng khác
    s = scored[scored["Year"] == year]
    if sens:
        s = s[~s["Indicator_ID"].isin(QUANT_IDS)]
    pv = (s.drop_duplicates(["Bank", "Indicator_ID"])
          .pivot(index="Indicator_ID", columns="Bank", values="Score_0_5"))
    if bank in pv.columns and pv.shape[1] > 1:
        me, peers = pv[bank], pv.drop(columns=[bank])
        peer_avg, peer_best = peers.mean(axis=1), peers.max(axis=1)
        best_bank = peers.fillna(-1).idxmax(axis=1)
        order = sorted(pv.index, key=_indicator_sort_key)

        def nm(i):
            return f"{i} {INDICATOR_NAME.get(i, '')}".strip()

        lead = (me - peer_avg).reindex(order).dropna().sort_values(ascending=False, kind="stable")
        for i, v in lead.items():
            if me[i] >= 3 and v >= 1.0 and len(S) < 4:
                S.append(f"{nm(i)}: {me[i]:.1f}, cao hơn TB các ngân hàng khác ({peer_avg[i]:.1f})")
        for i, v in lead.sort_values(kind="stable").items():
            if v <= -1.0 and len(W) < 4:
                tail = " (bằng chứng xác nhận chưa triển khai)" if me[i] == 0 else ""
                W.append(f"{nm(i)}: {me[i]:.1f}, thấp hơn TB các ngân hàng khác ({peer_avg[i]:.1f}){tail}")
        gap = (peer_best - me.fillna(0)).reindex(order).dropna().sort_values(ascending=False, kind="stable")
        for i, g in gap.items():
            if g >= 1.0 and peer_best[i] >= 3 and len(O) < 3:
                mine_txt = "chưa thấy bằng chứng công khai" if pd.isna(me[i]) else f"{me[i]:.1f}"
                O.append(f"{nm(i)}: bạn {mine_txt}, {best_bank[i]} đã đạt {peer_best[i]:.1f}. "
                         f"Có thể học hỏi để bắt kịp")

    # Thách thức: xu hướng
    prev_year = year - 1
    if prev_year in set(df["Year"]):
        prev = df[df["Year"] == prev_year].set_index("Bank")
        if bank in prev.index and len(prev) == len(cur) and int(row["Rank"]) > int(prev.loc[bank, "Rank"]):
            T.append(f"Thứ hạng giảm từ {int(prev.loc[bank, 'Rank'])} xuống {int(row['Rank'])} so với {prev_year}")
        sp = scored[(scored["Year"] == prev_year) & (scored["Bank"] == bank)].set_index("Indicator_ID")["Score_0_5"]
        sc_ = scored[(scored["Year"] == year) & (scored["Bank"] == bank)].set_index("Indicator_ID")["Score_0_5"]
        drops = (sc_ - sp.reindex(sc_.index)).dropna()
        if sens:
            drops = drops[~drops.index.isin(QUANT_IDS)]
        lost = [i for i in sc_.index if pd.isna(sc_[i]) and pd.notna(sp.get(i, np.nan))
                and not (sens and i in QUANT_IDS)]
        for i in sorted(lost, key=_indicator_sort_key):
            if len(T) < 3:
                T.append(f"{i} {INDICATOR_NAME.get(i, '')}: không còn thấy bằng chứng công khai năm {year} "
                         f"(năm {prev_year}: {sp[i]:.1f})")
        for i, v in drops.sort_values(kind="stable").items():
            if v <= -1.0 and len(T) < 3:
                T.append(f"{i} {INDICATOR_NAME.get(i, '')}: giảm từ {sp[i]:.1f} ({prev_year}) xuống {sc_[i]:.1f}")
    if year > FIRST:
        first = df[df["Year"] == FIRST].set_index("Bank")
        if bank in first.index:
            rel = {}
            for p in PILLARS:
                mine = row[p] - first.loc[bank, p]
                grp = (cur[p] - first[p]).mean()
                if pd.notna(mine) and pd.notna(grp):
                    rel[p] = (mine - grp, mine, grp)
            for p, (r_, mine, grp) in sorted(rel.items(), key=lambda kv: kv[1][0]):
                if r_ <= -0.05 and len(T) < 5:
                    T.append(f"{PILLAR_VN[p]}: thay đổi {mine:+.2f} từ {FIRST}, kém hơn mức thay đổi TB nhóm ({grp:+.2f})")
    return {"S": S, "W": W, "O": O, "T": T}


def fmt_delta(x):
    return f"{x:+.2f}"


def delta_class(x):
    return "up" if x > 0.005 else ("down" if x < -0.005 else "flat")


def delta_icon(x):
    return "🟢" if x > 0.005 else ("🔴" if x < -0.005 else "⚪")


# ==========================================================
# 3. THÀNH PHẦN GIAO DIỆN
# ==========================================================
def panel(children=None, title=None, hint=None, class_name="", **kw):
    head = []
    if title:
        head.append(html.H3(title, className="panel-title"))
    if hint:
        head.append(html.P(hint, className="panel-hint"))
    children = children or []
    return html.Div(head + (children if isinstance(children, list) else [children]),
                    className=f"panel {class_name}".strip(), **kw)


def graph(gid, **kw):
    return dcc.Graph(id=gid, config=GRAPH_CONFIG, **kw)


def year_options():
    return [{"label": f"Năm {y}", "value": y} for y in YEARS]


def pillar_options(with_all=True):
    opts = [{"label": "Tất cả trụ cột", "value": "ALL"}] if with_all else []
    return opts + [{"label": PILLAR_VN[p], "value": p} for p in PILLARS]


def atm_card(row, year, sens):
    bank = row["Bank"]
    moved = int(row["Rank_Full"]) - int(row["Rank"]) if sens else 0
    shift = f" ▲{moved}" if moved > 0 else (f" ▼{-moved}" if moved < 0 else "")
    rank = int(row["Rank"])
    return html.Div(
        className="atm-card" + (" is-top" if rank == 1 else ""),
        style={"background": ATM_BACKGROUNDS.get(bank, DEFAULT_ATM_BG)},
        children=[
            html.Div(className="atm-top", children=[
                html.Div(className="atm-chip"),
                html.Span(f"🏆 Hạng {rank}{shift}", className="atm-rank")]),
            html.Div(className="atm-mid", children=[
                html.Div(bank, className="atm-bank"),
                html.Div(BANK_NAMES.get(bank, ""), className="atm-fullname")]),
            html.Div(className="atm-bottom", children=[
                html.Div(f"•••• •••• •••• {year}", className="atm-number"),
                html.Div([html.Span(f"{row['Digital_Score']:.2f}", className="atm-score"),
                          html.Span(" / 5.0", className="atm-max")])]),
        ])


def bench_card(bank, row, avg):
    d_all = row["Digital_Score"] - avg["Digital_Score"]
    label = {"up": "Vượt", "down": "Dưới", "flat": "Ngang"}[delta_class(d_all)]
    chips = []
    for p in PILLARS:
        dl = row[p] - avg[p]
        chips.append(html.Span(
            f"{delta_icon(dl)} {PILLAR_VN[p]} {row[p]:.2f} ({fmt_delta(dl)})",
            className=f"chip {delta_class(dl)}"))
    return html.Div(className="bench-card", children=[
        html.Div(className="bench-head", children=[
            html.Span(bank, className="bench-bank", style={"borderColor": BANK_COLORS.get(bank, "#8B5CF6")}),
            html.Span(f"{row['Digital_Score']:.2f}", className="bench-score")]),
        html.Div(f"{delta_icon(d_all)} {label} TB Nhóm Top 5 ({fmt_delta(d_all)})",
                 className=f"badge {delta_class(d_all)}"),
        html.Div(chips, className="chip-row"),
    ])


def swot_card(key, title, items):
    body = ([html.Li(t) for t in items] if items
            else [html.Li("Chưa ghi nhận điểm nổi bật theo dữ liệu hiện có", className="muted")])
    return html.Div(className=f"swot swot-{key}", children=[
        html.Div(className="swot-head", children=[html.Span(key, className="swot-letter"),
                                                  html.Span(title, className="swot-title")]),
        html.Ul(body)])


# ==========================================================
# 4. APP & LAYOUT
# ==========================================================
app = dash.Dash(__name__, title="Digital Banking Index 2021–2025", suppress_callback_exceptions=True)
server = app.server

NAV = [("btn-tab1", "📊  Overview & Trend"),
       ("btn-tab2", "🎯  Pillar & Indicator"),
       ("btn-tab3", "🔍  Evidence & Quality"),
       ("btn-tab4", "🧭  Positioning & SWOT")]

app.layout = html.Div(className="app-shell", children=[
    dcc.Store(id="active-tab", data="btn-tab1"),
    dcc.Store(id="theme-store", data="light"),

    html.Aside(className="sidebar", children=[
        html.Div(className="brand", children=[
            html.Div("DBI", className="brand-mark"),
            html.Div([html.Div("Digital Banking Index", className="brand-name"),
                      html.Div("5 ngân hàng · 2021–2025", className="brand-sub")])]),
        html.Nav([html.Button(label, id=bid, className="nav-btn" + (" active" if bid == "btn-tab1" else ""),
                              n_clicks=0) for bid, label in NAV], className="nav"),
        html.P("Chỉ số rút gọn dựa trên dữ liệu công khai (public-data-based), không phải DBI chính thức. "
               "Cập nhật khi nguồn công khai được cập nhật; không phải dữ liệu realtime.",
               className="side-note"),
    ]),

    html.Main(className="main", children=[
        html.Header(className="topbar", children=[
            html.Div([html.H1("Mức độ chuyển đổi số ngân hàng", className="page-title"),
                      html.Div(id="scenario-note", className="scenario-note")]),
            html.Div(className="controls", children=[
                html.Div([html.Label("Năm", className="ctl-label"),
                          dcc.Dropdown(id="g-year", options=year_options(), value=LATEST,
                                       clearable=False, searchable=False, className="dd")], className="ctl"),
                dcc.Checklist(id="g-sens", className="switch",
                              options=[{"label": " Thử nghiệm loại bỏ 2 chỉ tiêu định lượng CUS2 & CUS3",
                                        "value": "on"}], value=[]),
                dcc.Checklist(id="g-theme", className="switch",
                              options=[{"label": " 🌙 Chế độ tối", "value": "dark"}], value=[]),
            ]),
        ]),
        html.Div(id="main-content"),
    ]),
])


def page_overview():
    return html.Div(className="page", children=[
        html.Div(id="p1-cards", className="atm-grid"),
        html.Div(id="p1-insight", className="insight"),
        panel([graph("p1-trend")]),
        panel([html.Div(id="p1-table")], title="Bảng xếp hạng chi tiết",
              hint="Điểm trụ cột là trung bình các tiêu chí hợp lệ; Digital Score là trung bình 6 trụ cột."),
    ])


def page_pillar():
    top2 = BANKS[:2]
    bank_opts = [{"label": b, "value": b} for b in BANKS]
    h2h_year_opts = [{"label": f"Năm {y}", "value": y} for y in YEARS] + \
                    [{"label": f"Cả {len(YEARS)} năm (xu hướng)", "value": "ALL"}]
    return html.Div(className="page", children=[
        panel(class_name="raised", children=[
            html.Div(className="filter-row", children=[
                html.Div([html.Label("Ngân hàng hiển thị trên radar và biểu đồ cột", className="ctl-label"),
                          dcc.Checklist(id="p2-banks", options=bank_opts, value=BANKS, inline=True,
                                        className="checks")], className="ctl grow")])]),
        html.Div(className="grid-2", children=[panel([graph("p2-radar")]), panel([graph("p2-stack")])]),
        panel(title="So với Trung bình Nhóm Khảo sát (Top 5 Average)",
              hint="Mỗi chip hiển thị điểm thực của trụ cột và chênh lệch so với trung bình 5 ngân hàng trong "
                   "nghiên cứu, không đại diện cho toàn ngành. Chênh lệch +0.00 nghĩa là điểm bằng trung bình nhóm.",
              children=[html.Div(id="p2-bench", className="bench-grid")]),
        panel(title="So sánh đối đầu (Head-to-Head)", class_name="raised", children=[
            html.Div(className="filter-row", children=[
                html.Div([html.Label("Ngân hàng A", className="ctl-label"),
                          dcc.Dropdown(id="h2h-a", options=bank_opts, value=top2[0] if top2 else None,
                                       clearable=False, searchable=False, className="dd")], className="ctl"),
                html.Div("vs", className="vs"),
                html.Div([html.Label("Ngân hàng B", className="ctl-label"),
                          dcc.Dropdown(id="h2h-b", options=bank_opts, value=top2[1] if len(top2) > 1 else None,
                                       clearable=False, searchable=False, className="dd")], className="ctl"),
                html.Div([html.Label("Năm so sánh", className="ctl-label"),
                          dcc.Dropdown(id="h2h-year", options=h2h_year_opts, value=LATEST,
                                       clearable=False, searchable=False, className="dd")],
                         className="ctl", style={"minWidth": "200px"}),
            ]),
            html.Div(className="grid-2 h2h", children=[html.Div(id="h2h-summary"), graph("h2h-chart")]),
        ]),
        panel(class_name="raised", title="Ma trận điểm từng tiêu chí", children=[
            html.Div(className="filter-row", children=[
                html.Div([html.Label("Lọc theo trụ cột", className="ctl-label"),
                          dcc.Dropdown(id="p2-pillar", options=pillar_options(), value="ALL",
                                       clearable=False, searchable=False, className="dd")],
                         className="ctl", style={"minWidth": "240px"}),
                dcc.Checklist(id="p2-hide-na", className="switch",
                              options=[{"label": " Ẩn tiêu chí chưa có dữ liệu (N/A ở mọi ngân hàng)",
                                        "value": "on"}], value=[]),
            ]),
            graph("p2-heatmap"),
            html.P(id="p2-heat-note", className="panel-hint"),
        ]),
    ])


def page_evidence():
    return html.Div(className="page", children=[
        panel(class_name="raised", title="Tra cứu bằng chứng gốc", children=[
            html.Div(className="filter-row", children=[
                html.Div([html.Label("Ngân hàng", className="ctl-label"),
                          dcc.Dropdown(id="p3-bank", clearable=False, searchable=False, className="dd",
                                       options=[{"label": "Tất cả ngân hàng", "value": "ALL"}] +
                                               [{"label": b, "value": b} for b in BANKS],
                                       value="ALL")], className="ctl"),
                html.Div([html.Label("Trụ cột", className="ctl-label"),
                          dcc.Dropdown(id="p3-pillar", options=pillar_options(), value="ALL",
                                       clearable=False, searchable=False, className="dd")], className="ctl"),
                html.Div([html.Label("Từ khóa (eKYC, Cloud, Core Banking…)", className="ctl-label"),
                          dcc.Input(id="p3-kw", type="text", debounce=False, className="search",
                                    placeholder="Gõ từ khóa để lọc đoạn trích dẫn")], className="ctl grow"),
                dcc.Checklist(id="p3-allyears", className="switch",
                              options=[{"label": " Xem tất cả các năm", "value": "on"}], value=[]),
            ]),
            html.Div(id="p3-count", className="result-count"),
            html.Div(id="p3-table"),
        ]),
        html.Div(className="grid-2", children=[panel([graph("p3-donut")]), panel([graph("p3-bar")])]),
        panel(title="Bảng chất lượng dữ liệu (data_quality.csv)", children=[
            dash_table.DataTable(
                data=dq_df.to_dict("records"), columns=[{"name": c, "id": c} for c in dq_df.columns],
                page_size=8, style_table={"overflowX": "auto"},
                style_header={"backgroundColor": "#8B5CF6", "color": "white", "fontWeight": "700",
                              "border": "none", "fontFamily": FONT},
                style_cell={"textAlign": "left", "fontFamily": FONT, "fontSize": "12.5px", "padding": "8px 10px",
                            "border": "none", "borderBottom": "1px solid var(--line)",
                            "backgroundColor": "transparent", "color": "var(--ink)"},
            ) if not dq_df.empty else html.P("Không tìm thấy data_quality.csv.", className="panel-hint"),
        ]),
    ])


def page_position():
    return html.Div(className="page", children=[
        panel(title="Bản đồ định vị",
              hint="Trục ngang là Digital Score của năm đang chọn; trục dọc là mức thay đổi so với đầu kỳ. "
                   "Hai đường nét đứt là trung bình của nhóm 5 ngân hàng.",
              children=[graph("pos-map"), html.Div(id="pos-chips", className="chip-row")]),
        panel(class_name="raised", title="Ma trận SWOT tương đối",
              hint="SWOT rút từ dữ liệu công khai khi so với nhóm 5 ngân hàng: S/W là vị thế so với trung bình nhóm, "
                   "O/T là khoảng cách với ngân hàng tốt nhất và xu hướng theo thời gian. "
                   "Đây là gợi ý định vị, không phải đánh giá nội bộ.",
              children=[
                  html.Div(className="filter-row", children=[
                      html.Div([html.Label("Chọn ngân hàng", className="ctl-label"),
                                dcc.Dropdown(id="swot-bank", options=[{"label": b, "value": b} for b in BANKS],
                                             value=BANKS[0], clearable=False, searchable=False,
                                             className="dd")], className="ctl")]),
                  html.Div(id="swot-grid", className="swot-grid")]),
    ])


PAGES = {"btn-tab1": page_overview, "btn-tab2": page_pillar, "btn-tab3": page_evidence,
         "btn-tab4": page_position}

# ==========================================================
# 5. CALLBACKS
# ==========================================================
@app.callback([Output("active-tab", "data")] + [Output(bid, "className") for bid, _ in NAV],
              [Input(bid, "n_clicks") for bid, _ in NAV])
def update_active_tab(*_):
    triggered = dash.callback_context.triggered
    bid = triggered[0]["prop_id"].split(".")[0] if triggered else "btn-tab1"
    if bid not in PAGES:
        bid = "btn-tab1"
    return (bid, *["nav-btn active" if k == bid else "nav-btn" for k, _ in NAV])


@app.callback(Output("main-content", "children"), Input("active-tab", "data"))
def render_tab(active):
    return PAGES.get(active, page_overview)()


@app.callback(Output("scenario-note", "children"), Input("g-sens", "value"))
def scenario_note(sens):
    n_scored = int(scored.loc[scored["Score_0_5"].notna(), "Indicator_ID"].nunique())
    if not sens:
        base = "Kịch bản đầy đủ: 24 tiêu chí"
        if n_scored < 24:
            base += f" ({n_scored} tiêu chí có điểm; tiêu chí N/A không tính vào trụ cột)"
        return base
    note = "Kịch bản kiểm tra độ nhạy: 22 tiêu chí (bỏ CUS2, CUS3)"
    if SENS_IDENTICAL:
        note += ". CUS2 và CUS3 hiện đều N/A nên kết quả trùng kịch bản đầy đủ"
    return note


# ---- Trang 1 ----
@app.callback([Output("p1-cards", "children"), Output("p1-insight", "children"),
               Output("p1-trend", "figure"), Output("p1-table", "children")],
              [Input("g-year", "value"), Input("g-sens", "value"), Input("g-theme", "value")])
def update_overview(year, sens_v, theme_v):
    sens, dark = bool(sens_v), bool(theme_v)
    df = get_scores(sens)
    d = df[df["Year"] == year].sort_values(["Rank", "Bank"])
    cards = [atm_card(r, year, sens) for _, r in d.iterrows()]

    insight = []
    if len(d) >= 2:
        gap = d.iloc[0]["Digital_Score"] - d.iloc[1]["Digital_Score"]
        insight.append(html.Div([
            html.Strong(f"Dẫn đầu {year}: {d.iloc[0]['Bank']} ({d.iloc[0]['Digital_Score']:.2f})"),
            html.Span(f"Hơn hạng 2 ({d.iloc[1]['Bank']}) {gap:.2f} điểm")]))
    unranked = [b for b in ALL_BANKS if b not in set(d["Bank"])]
    if unranked:
        insight.append(html.Div([
            html.Strong(f"Chưa xếp hạng năm {year}: {', '.join(unranked)}"),
            html.Span("Thiếu bằng chứng ở ít nhất một trụ cột (N/A), không bị tính 0 điểm")]))
    first = df[df["Year"] == FIRST].set_index("Bank")["Digital_Score"]
    last = df[df["Year"] == LATEST].set_index("Bank")["Digital_Score"]
    growth = (last - first).dropna().sort_values(ascending=False)
    if not growth.empty:
        insight.append(html.Div([
            html.Strong(f"Tăng nhiều nhất {FIRST}–{LATEST}: {growth.index[0]} ({growth.iloc[0]:+.2f})"),
            html.Span(f"Ít nhất: {growth.index[-1]} ({growth.iloc[-1]:+.2f})")]))

    t = d[["Rank", "Bank"] + PILLARS + ["Digital_Score"]].copy()
    t[PILLARS + ["Digital_Score"]] = t[PILLARS + ["Digital_Score"]].round(2)
    cols = [{"name": "Hạng", "id": "Rank"}, {"name": "Ngân hàng", "id": "Bank"}] + \
           [{"name": PILLAR_VN[p], "id": p} for p in PILLARS] + [{"name": "Digital Score", "id": "Digital_Score"}]
    if sens:
        t["Rank_Full"] = d["Rank_Full"].values
        t["Shift"] = [("▲" + str(rf - r)) if rf > r else (("▼" + str(r - rf)) if rf < r else "–")
                      for rf, r in zip(d["Rank_Full"], d["Rank"])]
        cols += [{"name": "Hạng (24 TC)", "id": "Rank_Full"}, {"name": "Thay đổi", "id": "Shift"}]
    table = dash_table.DataTable(
        data=t.to_dict("records"), columns=cols, style_table={"overflowX": "auto"},
        style_header={"backgroundColor": "#8B5CF6", "color": "white", "fontWeight": "700", "border": "none",
                      "fontFamily": FONT, "textAlign": "center"},
        style_cell={"textAlign": "center", "fontFamily": FONT, "fontSize": "13.5px", "padding": "11px",
                    "border": "none", "borderBottom": "1px solid var(--line)",
                    "backgroundColor": "transparent", "color": "var(--ink)"},
        style_cell_conditional=[{"if": {"column_id": "Bank"}, "textAlign": "left", "fontWeight": "700"}],
        style_data_conditional=[
            {"if": {"filter_query": "{Rank} = 1"}, "backgroundColor": "rgba(224,86,199,0.10)", "fontWeight": "700"},
            {"if": {"column_id": "Digital_Score"}, "fontWeight": "800", "color": "var(--accent-text)"}])
    return cards, insight, fig_trend(sens, dark), table


# ---- Trang 2 ----
@app.callback([Output("p2-radar", "figure"), Output("p2-stack", "figure"), Output("p2-bench", "children")],
              [Input("g-year", "value"), Input("g-sens", "value"), Input("p2-banks", "value"),
               Input("g-theme", "value")])
def update_pillar_charts(year, sens_v, banks, theme_v):
    sens, banks, dark = bool(sens_v), banks or [], bool(theme_v)
    d = get_scores(sens)
    d = d[d["Year"] == year]
    avg = d[PILLARS + ["Digital_Score"]].mean()
    bench = [bench_card(b, d[d["Bank"] == b].iloc[0], avg)
             for b in BANKS if b in banks and not d[d["Bank"] == b].empty]
    if not bench:
        bench = [html.P("Chọn ít nhất một ngân hàng để xem so sánh.", className="panel-hint")]
    else:
        bench.insert(0, html.Div(f"Trung bình {len(d)} NH có điểm năm {year}: {avg['Digital_Score']:.2f}",
                                 className="bench-avg"))
    return (fig_radar(year, banks, sens, f"Sáu trụ cột năm {year}", dark),
            fig_stacked(year, banks, sens, dark), bench)


@app.callback([Output("p2-heatmap", "figure"), Output("p2-heat-note", "children")],
              [Input("g-year", "value"), Input("g-sens", "value"),
               Input("p2-pillar", "value"), Input("p2-hide-na", "value"), Input("g-theme", "value")])
def update_heatmap(year, sens_v, pillar, hide_na, theme_v):
    sens = bool(sens_v)
    return fig_heatmap(year, pillar, sens, bool(hide_na), bool(theme_v)), heat_note(year, pillar, sens)


@app.callback([Output("h2h-summary", "children"), Output("h2h-chart", "figure")],
              [Input("g-sens", "value"), Input("h2h-a", "value"), Input("h2h-b", "value"),
               Input("h2h-year", "value"), Input("g-theme", "value")])
def update_h2h(sens_v, a, b, year, theme_v):
    sens, dark = bool(sens_v), bool(theme_v)
    if not a or not b or a == b:
        return html.P("Chọn hai ngân hàng khác nhau để so sánh.", className="panel-hint"), go.Figure()
    df = get_scores(sens)

    # --- Chế độ cả 5 năm ---
    if year == "ALL":
        rows, wa, wb = [], 0, 0
        for y in sorted(YEARS):
            dy = df[df["Year"] == y].set_index("Bank")
            if a not in dy.index or b not in dy.index:
                continue
            sa, sb = dy.loc[a, "Digital_Score"], dy.loc[b, "Digital_Score"]
            wa, wb = wa + (sa > sb), wb + (sb > sa)
            rows.append(html.Tr([html.Td(str(y)), html.Td(f"{sa:.2f}"), html.Td(f"{sb:.2f}"),
                                 html.Td(f"{sa - sb:+.2f}", className=delta_class(sa - sb))]))
        head = f"{FIRST}–{LATEST}: {a} dẫn trước {wa} năm, {b} dẫn trước {wb} năm"
        table = html.Table(className="h2h-table", children=[
            html.Thead(html.Tr([html.Th("Năm"), html.Th(a), html.Th(b), html.Th(f"{a} − {b}")])),
            html.Tbody(rows)])
        return html.Div(className="h2h-box", children=[html.Div(head, className="h2h-head"), table]), \
            fig_h2h_trend(a, b, sens, dark)

    # --- Chế độ một năm ---
    d = df[df["Year"] == year].set_index("Bank")
    if a not in d.index or b not in d.index:
        return html.P("Thiếu dữ liệu cho năm đã chọn.", className="panel-hint"), go.Figure()
    diff = d.loc[a, "Digital_Score"] - d.loc[b, "Digital_Score"]
    if abs(diff) < 0.005:
        head = f"{a} và {b} ngang điểm ({d.loc[a, 'Digital_Score']:.2f}) năm {year}"
    else:
        win, lose = (a, b) if diff > 0 else (b, a)
        head = f"Năm {year}: {win} cao hơn {lose} {abs(diff):.2f} điểm Digital Score"

    s = scored[(scored["Year"] == year) & scored["Bank"].isin([a, b])]
    if sens:
        s = s[~s["Indicator_ID"].isin(QUANT_IDS)]
    pv = (s.drop_duplicates(["Bank", "Indicator_ID"]).pivot(index="Indicator_ID", columns="Bank",
                                                            values="Score_0_5")
          .reindex(columns=[a, b]).dropna())
    pv["diff"] = pv[a] - pv[b]

    def lines(sub, w, l):
        if sub.empty:
            return [html.Li("Không có tiêu chí nào", className="muted")]
        return [html.Li([html.Strong(f"{i} "), INDICATOR_NAME.get(i, ""),
                         html.Span(f"  {r[w]:.1f} vs {r[l]:.1f}", className="muted")])
                for i, r in sub.iterrows()]

    a_win = pv[pv["diff"] > 0].sort_values("diff", ascending=False, kind="stable").head(3)
    b_win = pv[pv["diff"] < 0].sort_values("diff", kind="stable").head(3)
    summary = html.Div(className="h2h-box", children=[
        html.Div(head, className="h2h-head"),
        html.H4(f"Top 3 tiêu chí {a} hơn {b}", className="h2h-sub"), html.Ol(lines(a_win, a, b)),
        html.H4(f"Top 3 tiêu chí {b} hơn {a}", className="h2h-sub"), html.Ol(lines(b_win, b, a)),
    ])
    return summary, fig_radar(year, [a, b], sens, f"{a} và {b} năm {year}", dark)


# ---- Trang 3 ----
@app.callback([Output("p3-count", "children"), Output("p3-table", "children"),
               Output("p3-donut", "figure"), Output("p3-bar", "figure")],
              [Input("g-year", "value"), Input("p3-bank", "value"), Input("p3-pillar", "value"),
               Input("p3-kw", "value"), Input("p3-allyears", "value"), Input("g-theme", "value")])
def update_evidence(year, bank, pillar, kw, allyears, theme_v):
    all_years, dark = bool(allyears), bool(theme_v)
    t = theme(dark)

    def scope(df):
        if not all_years:
            df = df[df["Year"] == year]
        if bank and bank != "ALL":
            df = df[df["Bank"] == bank]
        if pillar and pillar != "ALL":
            df = df[df["PillarKey"] == pillar]
        return df

    ev = scope(EVID)
    kw_clean = (kw or "").strip().lower()
    if kw_clean:
        ev = ev[ev["_search"].str.contains(re.escape(kw_clean), na=False)]
    ev = ev.assign(_k=ev["Indicator_ID"].map(_indicator_sort_key)).sort_values(
        ["Year", "Bank", "_k"], ascending=[False, True, True])
    show = ev[EVID_SHOW_COLS].copy()
    if "Score_0_5" in show.columns:
        show["Score_0_5"] = show["Score_0_5"].astype(object).where(show["Score_0_5"].notna(), "N/A")
    count = f"{len(show)} dòng bằng chứng" + (f' khớp "{kw.strip()}"' if kw_clean else "")
    if show.empty:
        table = html.P("Không có bằng chứng khớp bộ lọc. Thử bỏ từ khóa hoặc chọn thêm năm.", className="panel-hint")
    else:
        table = dash_table.DataTable(
            data=show.to_dict("records"),
            columns=[{"name": EVID_HEADER.get(c, c.replace("_", " ")), "id": c} for c in EVID_SHOW_COLS],
            page_size=8, style_table={"overflowX": "auto"},
            style_header={"backgroundColor": "#8B5CF6", "color": "white", "fontWeight": "700",
                          "border": "none", "fontFamily": FONT},
            style_cell={"textAlign": "left", "fontFamily": FONT, "fontSize": "12.5px", "padding": "10px",
                        "border": "none", "borderBottom": "1px solid var(--line)",
                        "backgroundColor": "transparent", "color": "var(--ink)", "verticalAlign": "top",
                        "minWidth": "70px", "maxWidth": "200px", "whiteSpace": "normal", "height": "auto"},
            style_cell_conditional=[
                {"if": {"column_id": "Evidence"}, "minWidth": "340px", "maxWidth": "480px"},
                {"if": {"column_id": "Indicator"}, "minWidth": "150px"},
                {"if": {"column_id": "Score_0_5"}, "minWidth": "80px"},
                {"if": {"column_id": "Source_Link"}, "maxWidth": "160px", "overflow": "hidden",
                 "textOverflow": "ellipsis"}],
            style_data_conditional=[
                {"if": {"filter_query": '{Evidence} contains "NOT_FOUND"'}, "color": "#9A8FBF"},
                {"if": {"column_id": "Score_0_5"}, "fontWeight": "800", "color": "var(--accent-text)"}])

    sc = scope(scored)
    na = int(sc["Score_0_5"].isna().sum())
    scored_rows = sc[sc["Score_0_5"].notna()]
    zero = int(((scored_rows["Score_0_5"] == 0) & ~scored_rows["Indicator_ID"].isin(QUANT_IDS)).sum())
    found = len(scored_rows) - zero
    total = found + zero + na
    rate = f"{found / total:.0%}" if total else "–"
    donut = go.Figure(go.Pie(
        labels=["Có bằng chứng, đã chấm điểm (1–5)", "Bằng chứng xác nhận chưa triển khai (điểm 0)",
                "N/A (không tìm thấy bằng chứng công khai hoặc thiếu số liệu so sánh)"],
        values=[found, zero, na], hole=0.62, sort=False,
        marker=dict(colors=["#8B5CF6", "#F472B6", t["na_slice"]], line=dict(color=t["pie_edge"], width=2)),
        textinfo="value", hovertemplate="%{label}<br>%{value} tiêu chí (%{percent})<extra></extra>"))
    donut.update_layout(**base_layout(
        dark, title=title_dict("Tỷ lệ tìm thấy dữ liệu công khai", dark), height=400,
        legend=dict(orientation="h", y=-0.1, x=0.5, xanchor="center", font=dict(size=11)),
        annotations=[dict(text=f"<b>{rate}</b><br>có điểm<br>(trên tổng tiêu chí)", x=0.5, y=0.5, showarrow=False,
                          font=dict(size=20, family=FONT, color=t["ink"]))]))

    cnt = scope(EVID)
    cnt = cnt[cnt["Is_Valid_Evidence"]].groupby(["Year", "Bank"]).size().reset_index(name="n")
    bar = go.Figure()
    for b in BANKS:
        sub = cnt[cnt["Bank"] == b].sort_values("Year")
        bar.add_trace(go.Bar(x=sub["Year"], y=sub["n"], name=b, marker_color=BANK_COLORS.get(b, "#8B5CF6"),
                             hovertemplate=b + " %{x}: %{y} bằng chứng<extra></extra>"))
    bar.update_layout(**base_layout(
        dark, title=title_dict("Số bằng chứng hợp lệ theo năm và ngân hàng", dark), barmode="group", height=400,
        xaxis=dict(tickmode="linear", dtick=1), yaxis=dict(title="Số bằng chứng", gridcolor=t["grid"])))
    return count, table, donut, bar


# ---- Trang 4 ----
@app.callback([Output("pos-map", "figure"), Output("pos-chips", "children")],
              [Input("g-year", "value"), Input("g-sens", "value"), Input("g-theme", "value")])
def update_position(year, sens_v, theme_v):
    sens = bool(sens_v)
    d = pos_data(year, sens)
    xm, ym = d["x"].mean(), d["y"].mean()
    chips = []
    if not d.empty:
        for bank, r in d.sort_values("rank").iterrows():
            chips.append(html.Span(f"{bank}: {quadrant_of(r['x'], r['y'], xm, ym)}", className="chip flat"))
    return fig_positioning(year, sens, bool(theme_v)), chips


@app.callback(Output("swot-grid", "children"),
              [Input("g-year", "value"), Input("g-sens", "value"), Input("swot-bank", "value")])
def update_swot(year, sens_v, bank):
    res = build_swot(bank, year, bool(sens_v))
    if res is None:
        return html.P("Thiếu dữ liệu cho lựa chọn này.", className="panel-hint")
    return [swot_card("S", "Điểm mạnh (so với nhóm)", res["S"]),
            swot_card("W", "Điểm yếu (so với nhóm)", res["W"]),
            swot_card("O", "Cơ hội (học hỏi từ ngân hàng dẫn đầu tiêu chí)", res["O"]),
            swot_card("T", "Thách thức (xu hướng và vị thế)", res["T"])]


# ---- Chế độ tối: đặt thuộc tính data-theme lên <html> (CSS đổi màu theo biến) ----
app.clientside_callback(
    """function(v) {
        var t = (v && v.length) ? 'dark' : 'light';
        document.documentElement.setAttribute('data-theme', t);
        return t;
    }""",
    Output("theme-store", "data"), Input("g-theme", "value"))


if __name__ == "__main__":
    import subprocess

    # 1. Tự động chạy lại Pipeline để cập nhật dữ liệu mới từ auto_score & clean_raw_data
    try:
        print("\n[INFO] Đang tự động chạy Pipeline cập nhật dữ liệu mới...")
        subprocess.run(["python", "clean_raw_data.py"], check=True)
        subprocess.run(["python", "auto_score.py"], check=True)
        subprocess.run(["python", "scoring.py"], check=True)
        print("✅ Đã cập nhật xong dữ liệu mới nhất vào CSV!\n")
    except Exception as e:
        print(f"[CẢNH BÁO] Không thể tự động chạy pipeline: {e}\n")

    # 2. Nạp cổng linh hoạt (hỗ trợ cả Localhost lẫn Deploy Cloud)
    host = "0.0.0.0" if os.environ.get("PORT") else "127.0.0.1"
    port = int(os.environ.get("PORT", 8050))
    app.run(debug=True, host=host, port=port)