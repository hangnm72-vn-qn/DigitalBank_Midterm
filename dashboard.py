import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Cấu hình trang
st.set_page_config(page_title="Digital Banking Index Dashboard", layout="wide")

FONT_FAMILY = "Times New Roman, serif"

# ==========================================
# 1. HÀM VẼ BIỂU ĐỒ (PLOTLY CHARTS)
# ==========================================

def create_trend_line_chart(final_scores_df):
    """Biểu đồ đường xu hướng Digital Score 2021-2025"""
    fig = px.line(
        final_scores_df,
        x='Year',
        y='Digital_Score',
        color='Bank',
        markers=True,
        title='Diễn biến Digital Score giai đoạn 2021 - 2025',
        labels={'Digital_Score': 'Điểm Chuyển đổi số', 'Year': 'Năm', 'Bank': 'Ngân hàng'}
    )
    fig.update_layout(
        font=dict(family=FONT_FAMILY, size=18, color='#000000'),
        title=dict(font=dict(size=26, family=FONT_FAMILY, color='#000000')),
        xaxis=dict(tickmode='linear', dtick=1, title_font=dict(size=20, color='#000000'), tickfont=dict(size=18, color='#000000')),
        yaxis=dict(title_font=dict(size=20, color='#000000'), tickfont=dict(size=18, color='#000000')),
        legend=dict(font=dict(size=18, color='#000000'), title=dict(font=dict(size=18, color='#000000'))),
        hovermode='x unified',
        template='plotly_white',
        height=550,
        margin=dict(l=40, r=40, t=60, b=40)
    )
    return fig

def create_pillar_radar_chart(final_scores_df, selected_year, selected_banks):
    """Biểu đồ Radar so sánh các trụ cột theo năm"""
    df_filtered = final_scores_df[(final_scores_df['Year'] == selected_year) & (final_scores_df['Bank'].isin(selected_banks))]
    
    exclude_cols = ['Bank', 'Year', 'Digital_Score', 'Pillars_Available', 'Rank']
    pillars = [col for col in final_scores_df.columns if col not in exclude_cols]
    
    fig = go.Figure()

    for _, row in df_filtered.iterrows():
        values = [row[p] for p in pillars]
        values.append(values[0])
        fig.add_trace(go.Scatterpolar(
            r=values,
            theta=pillars + [pillars[0]],
            fill='toself',
            name=row['Bank']
        ))

    fig.update_layout(
        font=dict(family=FONT_FAMILY, size=16, color='#000000'),
        title=dict(text=f'So sánh Trụ cột Chuyển đổi số năm {selected_year}', font=dict(size=24, family=FONT_FAMILY, color='#000000')),
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 5], tickfont=dict(size=16, color='#000000')),
            angularaxis=dict(tickfont=dict(size=18, color='#000000'))
        ),
        legend=dict(font=dict(size=18, color='#000000')),
        showlegend=True,
        height=580,
        margin=dict(l=40, r=40, t=60, b=40)
    )
    return fig

def create_indicator_heatmap(scored_data_df, selected_year):
    """Heatmap Plotly kích thước siêu to, tràn màn hình, rõ chữ"""
    df_filtered = scored_data_df[scored_data_df['Year'] == selected_year].copy()
    pivot_df = df_filtered.pivot(index='Indicator_ID', columns='Bank', values='Score_0_5')
    
    fig = px.imshow(
        pivot_df,
        labels=dict(x="Ngân hàng", y="Mã Tiêu chí", color="Điểm (0-5)"),
        x=pivot_df.columns,
        y=pivot_df.index,
        color_continuous_scale='Blues',
        text_auto='.1f',
        title=f'Heatmap Điểm Chi tiết 24 Tiêu chí (Năm {selected_year})'
    )
    fig.update_layout(
        font=dict(family=FONT_FAMILY, size=18, color='#000000'),
        title=dict(font=dict(size=26, family=FONT_FAMILY, color='#000000')),
        xaxis=dict(title_font=dict(size=20, color='#000000'), tickfont=dict(size=18, color='#000000'), side='bottom'),
        yaxis=dict(title_font=dict(size=20, color='#000000'), tickfont=dict(size=16, color='#000000'), dtick=1),
        coloraxis_colorbar=dict(title=dict(font=dict(size=18, color='#000000')), tickfont=dict(size=16, color='#000000')),
        height=750,
        margin=dict(l=60, r=60, t=80, b=60)
    )
    fig.update_xaxes(scaleanchor=None)
    fig.update_yaxes(scaleratio=None)
    return fig

# ==========================================
# 2. CSS TÙY CHỈNH GIAO DIỆN & FONT
# ==========================================
custom_css = """
<style>
    /* Ép Font Times New Roman & Tăng cỡ chữ cơ sở lên 20px, màu đen */
    html, body, [class*="css"], .stMarkdown, .stSelectbox, .stMultiSelect, p, span, label, div {
        font-family: 'Times New Roman', Times, serif !important;
        font-size: 20px !important;
        color: #000000 !important;
    }
    
    /* Banner Header */
    .header-banner {
        background: linear-gradient(135deg, #0F172A 0%, #1E3A8A 100%);
        padding: 26px 32px;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.2);
        margin-bottom: 25px;
    }
    .header-title {
        font-size: 38px !important;
        font-weight: bold !important;
        color: #FFFFFF !important;
        margin: 0 !important;
        font-family: 'Times New Roman', Times, serif !important;
    }
    .header-subtitle {
        font-size: 20px !important;
        color: #F1F5F9 !important;
        margin-top: 8px !important;
    }

    /* Tiêu đề H1, H2, H3 màu đen đậm rõ nét */
    h1 { font-size: 36px !important; font-weight: bold !important; color: #000000 !important; }
    h2 { font-size: 30px !important; font-weight: bold !important; color: #000000 !important; }
    h3 { font-size: 24px !important; font-weight: bold !important; color: #000000 !important; }

    /* Thẻ Metric Bảng xếp hạng */
    .metric-card {
        background-color: #F8FAFC;
        border: 2px solid #CBD5E1;
        border-radius: 10px;
        padding: 18px;
        text-align: center;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
    }
    .metric-rank { font-size: 20px; font-weight: bold; color: #334155; }
    .metric-bank { font-size: 26px; font-weight: bold; color: #000000; margin: 6px 0; }
    .metric-score { font-size: 36px; font-weight: bold; color: #1D4ED8; }

    /* Tab tiêu đề cỡ lớn */
    button[data-baseweb="tab"] div p {
        font-size: 22px !important;
        font-weight: bold !important;
        color: #000000 !important;
    }

    /* Bảng st.dataframe: Tiêu đề cột đen đậm, chữ to */
    [data-testid="stDataFrame"] { font-size: 19px !important; }
    th {
        background-color: #E2E8F0 !important;
        color: #000000 !important;
        font-size: 20px !important;
        font-weight: bold !important;
    }
    td { color: #000000 !important; font-size: 19px !important; }
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# BANNER HEADER
st.markdown("""
<div class="header-banner">
    <div class="header-title">🏦 Dashboard Đánh giá Mức độ Chuyển đổi số Ngân hàng (2021 - 2025)</div>
    <div class="header-subtitle">Hệ thống phân tích & tra cứu chỉ số Digital Banking Index từ nguồn dữ liệu công khai</div>
</div>
""", unsafe_allow_html=True)

# ==========================================
# 3. NẠP DỮ LIỆU (DATA LOADING)
# ==========================================
@st.cache_data
def load_data():
    final_scores = pd.read_csv('final_scores.csv')
    scored_data = pd.read_csv('scored_data.csv')
    raw_data = pd.read_csv('raw_data.csv')
    data_quality = pd.read_csv('data_quality.csv')
    return final_scores, scored_data, raw_data, data_quality

try:
    final_scores_df, scored_data_df, raw_data_df, data_quality_df = load_data()
except Exception as e:
    st.error(f"Lỗi tải dữ liệu: {e}. Vui lòng kiểm tra lại các file CSV trong thư mục.")
    st.stop()

# Đặt các Tab
tab1, tab2, tab3 = st.tabs([
    "📊 Trang 1: Overview & Trend", 
    "🎯 Trang 2: Pillar & Indicator", 
    "🔍 Trang 3: Evidence & Data Quality"
])

# ==========================================
# TRANG 1: OVERVIEW & TREND
# ==========================================
with tab1:
    st.header("Tổng quan & Xu hướng (2021 - 2025)")
    
    col_year, _ = st.columns([1, 3])
    with col_year:
        years = sorted(final_scores_df['Year'].unique(), reverse=True)
        selected_year = st.selectbox("Chọn Năm xem xếp hạng:", years, index=0)
    
    st.subheader(f"🏆 Bảng Xếp hạng Digital Score năm {selected_year}")
    df_year = final_scores_df[final_scores_df['Year'] == selected_year].sort_values(by='Rank')
    
    cols = st.columns(len(df_year))
    for idx, (_, row) in enumerate(df_year.iterrows()):
        with cols[idx]:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-rank">Hạng {int(row['Rank'])}</div>
                <div class="metric-bank">{row['Bank']}</div>
                <div class="metric-score">{row['Digital_Score']:.2f} <span style="font-size:18px; color:#475569;">/ 5.0</span></div>
            </div>
            """, unsafe_allow_html=True)
            
    st.markdown("<br>", unsafe_allow_html=True)
    display_cols = [c for c in df_year.columns if c != 'Pillars_Available']
    st.dataframe(df_year[display_cols], use_container_width="stretch")
    
    st.markdown("---")
    st.plotly_chart(create_trend_line_chart(final_scores_df), use_container_width="stretch")

# ==========================================
# TRANG 2: PILLAR & INDICATOR
# ==========================================
with tab2:
    st.header("Phân tích Trụ cột & Tiêu chí")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("Bộ lọc Phân tích")
        p2_year = st.selectbox("Chọn Năm:", sorted(final_scores_df['Year'].unique(), reverse=True), key='p2_y')
        all_banks = final_scores_df['Bank'].unique().tolist()
        selected_banks = st.multiselect("Chọn Ngân hàng:", all_banks, default=all_banks)
        
    with col2:
        if selected_banks:
            fig_radar = create_pillar_radar_chart(final_scores_df, p2_year, selected_banks)
            st.plotly_chart(fig_radar, use_container_width="stretch")
        else:
            st.warning("Vui lòng chọn ít nhất một ngân hàng.")

    st.markdown("---")
    st.subheader(f"📊 Heatmap Bảng điểm Chi tiết 24 Tiêu chí (Năm {p2_year})")
    fig_heatmap = create_indicator_heatmap(scored_data_df, p2_year)
    st.plotly_chart(fig_heatmap, use_container_width="stretch")

# ==========================================
# TRANG 3: EVIDENCE & DATA QUALITY
# ==========================================
with tab3:
    st.header("Bằng chứng dữ liệu (Evidence) & Chất lượng Dữ liệu")
    
    subtab1, subtab2 = st.tabs(["🔎 Tra cứu Bằng chứng (Evidence)", "📈 Chất lượng Dữ liệu (Data Quality)"])
    
    with subtab1:
        st.subheader("Bộ lọc tra cứu dữ liệu gốc")
        f_col1, f_col2, f_col3 = st.columns(3)
        with f_col1:
            bank_f = st.selectbox("Ngân hàng:", ["Tất cả"] + list(raw_data_df['Bank'].unique()))
        with f_col2:
            year_f = st.selectbox("Năm:", ["Tất cả"] + list(sorted(raw_data_df['Year'].unique(), reverse=True)))
        with f_col3:
            pillar_f = st.selectbox("Trụ cột:", ["Tất cả"] + list(raw_data_df['Pillar'].unique()))
            
        filtered_raw = raw_data_df.copy()
        if bank_f != "Tất cả":
            filtered_raw = filtered_raw[filtered_raw['Bank'] == bank_f]
        if year_f != "Tất cả":
            filtered_raw = filtered_raw[filtered_raw['Year'] == year_f]
        if pillar_f != "Tất cả":
            filtered_raw = filtered_raw[filtered_raw['Pillar'] == pillar_f]
            
        st.dataframe(filtered_raw, use_container_width="stretch")

    with subtab2:
        st.subheader("Báo cáo Chất lượng Dữ liệu (Data Quality)")
        st.dataframe(data_quality_df, use_container_width="stretch")