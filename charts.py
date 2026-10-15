import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

FONT_FAMILY = "Times New Roman, serif"

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
    
    # Pivot lấy dữ liệu
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