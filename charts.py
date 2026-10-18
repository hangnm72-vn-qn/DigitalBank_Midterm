import os
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Khai báo font chữ chuẩn dùng cho báo cáo (Times New Roman / Plus Jakarta Sans)
FONT_FAMILY = "Times New Roman, 'Plus Jakarta Sans', Arial, sans-serif"

def create_trend_line_chart(final_scores_df):
    """Biểu đồ đường xu hướng Digital Score 2021-2025 cho báo cáo"""
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
        title=dict(font=dict(size=24, family=FONT_FAMILY, color='#000000'), x=0.02),
        xaxis=dict(
            tickmode='linear', 
            dtick=1, 
            title_font=dict(size=18, color='#000000', family=FONT_FAMILY), 
            tickfont=dict(size=16, color='#000000', family=FONT_FAMILY)
        ),
        yaxis=dict(
            title_font=dict(size=18, color='#000000', family=FONT_FAMILY), 
            tickfont=dict(size=16, color='#000000', family=FONT_FAMILY),
            range=[0, 5.2]
        ),
        legend=dict(
            font=dict(size=16, color='#000000', family=FONT_FAMILY), 
            title=dict(font=dict(size=16, color='#000000', family=FONT_FAMILY))
        ),
        hovermode='x unified',
        template='plotly_white',
        height=550,
        margin=dict(l=50, r=50, t=70, b=50)
    )
    return fig

def create_pillar_radar_chart(final_scores_df, selected_year, selected_banks):
    """Biểu đồ Radar so sánh các trụ cột theo năm"""
    df_filtered = final_scores_df[
        (final_scores_df['Year'] == selected_year) & 
        (final_scores_df['Bank'].isin(selected_banks))
    ]
    
    pillars = ['Customer', 'Strategy', 'Technology', 'Operations', 'Culture', 'Data']
    pillar_vn = ['Khách hàng', 'Chiến lược', 'Công nghệ', 'Vận hành', 'Văn hóa', 'Dữ liệu']
    
    fig = go.Figure()

    for _, row in df_filtered.iterrows():
        values = [row[p] if p in row and pd.notna(row[p]) else 0 for p in pillars]
        values.append(values[0])  # Khép kín đường Radar
        
        fig.add_trace(go.Scatterpolar(
            r=values,
            theta=pillar_vn + [pillar_vn[0]],
            fill='toself',
            name=row['Bank']
        ))

    fig.update_layout(
        font=dict(family=FONT_FAMILY, size=16, color='#000000'),
        title=dict(
            text=f'So sánh Trụ cột Chuyển đổi số năm {selected_year}', 
            font=dict(size=24, family=FONT_FAMILY, color='#000000'),
            x=0.02
        ),
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 5], tickfont=dict(size=14, color='#000000', family=FONT_FAMILY)),
            angularaxis=dict(tickfont=dict(size=16, color='#000000', family=FONT_FAMILY))
        ),
        legend=dict(font=dict(size=16, color='#000000', family=FONT_FAMILY)),
        showlegend=True,
        template='plotly_white',
        height=580,
        margin=dict(l=50, r=50, t=70, b=50)
    )
    return fig

def create_indicator_heatmap(scored_data_df, selected_year):
    """Heatmap Plotly hiển thị điểm phân hóa từ auto_score và Min-Max CUS2/CUS3"""
    df_filtered = scored_data_df[scored_data_df['Year'] == selected_year].copy()
    
    # Pivot tạo ma trận điểm 24 tiêu chí
    pivot_df = df_filtered.pivot(index='Indicator_ID', columns='Bank', values='Score_0_5')
    
    fig = px.imshow(
        pivot_df,
        labels=dict(x="Ngân hàng", y="Mã Tiêu chí", color="Điểm (0-5)"),
        x=pivot_df.columns,
        y=pivot_df.index,
        color_continuous_scale='Purples',
        text_auto='.1f',
        title=f'Heatmap Điểm Chi tiết 24 Tiêu chí (Năm {selected_year})',
        zmin=0,
        zmax=5
    )
    fig.update_layout(
        font=dict(family=FONT_FAMILY, size=16, color='#000000'),
        title=dict(font=dict(size=24, family=FONT_FAMILY, color='#000000'), x=0.02),
        xaxis=dict(
            title_font=dict(size=18, color='#000000', family=FONT_FAMILY), 
            tickfont=dict(size=16, color='#000000', family=FONT_FAMILY), 
            side='bottom'
        ),
        yaxis=dict(
            title_font=dict(size=18, color='#000000', family=FONT_FAMILY), 
            tickfont=dict(size=14, color='#000000', family=FONT_FAMILY), 
            dtick=1
        ),
        coloraxis_colorbar=dict(
            title=dict(text="Điểm", font=dict(size=16, color='#000000', family=FONT_FAMILY)), 
            tickfont=dict(size=14, color='#000000', family=FONT_FAMILY)
        ),
        template='plotly_white',
        height=750,
        margin=dict(l=60, r=60, t=80, b=60)
    )
    return fig