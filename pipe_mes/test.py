import streamlit as st
import pandas as pd
import plotly.express as px

# 페이지 기본 설정
st.set_page_config(page_title="호선별 진행 상황 대시보드", layout="wide")

st.title("🚢 호선별 공정 진행 상황 (MES)")
st.markdown("---")

# ------------------------------------------------------------------
# 1. 예시 데이터 생성 (실제 DB 연결 시 이 부분을 쿼리 결과 데이터프레임으로 대체)
# ------------------------------------------------------------------
data = {
    "호선": ["sn101", "sn201", "sn301"],
    "진행률(%)": [85, 45, 15],          # 공정 진행률
    "총_설계_중량(kg)": [15000, 18000, 12000],
    "현재_설치_중량(kg)": [12750, 8100, 1800],
    "상태": ["마감 단계", "의장 작업 중", "착공 단계"]
}
df = pd.DataFrame(data)

# ------------------------------------------------------------------
# 2. 상단: 호선별 진행 상황 (프로그레스 바 & 메트릭)
# ------------------------------------------------------------------
st.subheader("📌 호선별 진행률 (Progress Status)")

# 3개 호선을 가로로 3컬럼으로 나누어 배치
cols = st.columns(3)

for idx, row in df.iterrows():
    with cols[idx]:
        # 호선 카드 스타일 상자
        st.markdown(f"### 🛳️ {row['호선'].upper()}")
        st.caption(f"상태: **{row['상태']}**")
        
        # 진행률 메트릭 표시
        st.metric(
            label="공정 진행률", 
            value=f"{row['진행률(%)']}%",
            delta=f"{row['현재_설치_중량(kg)']:,.0f} / {row['총_설계_중량(kg)']:,.0f} kg"
        )
        
        # 진행률 바 (Progress Bar)
        st.progress(row['진행률(%)'] / 100)
        st.write("") # 간격 조정

st.markdown("---")

# ------------------------------------------------------------------
# 3. 하단: 인터랙티브 비교 그래프 (Plotly)
# ------------------------------------------------------------------
col_left, col_right = st.columns([1, 1])

with col_left:
    st.subheader("📊 호선별 진행률 비교 (Bar Chart)")
    
    # 가로 막대 그래프 생성
    fig_progress = px.bar(
        df,
        x="진행률(%)",
        y="호선",
        orientation='h',
        text="진행률(%)",
        color="진행률(%)",
        color_continuous_scale="Blues", # 푸른색 계열 테마
        range_x=[0, 100]
    )
    
    # 막대 안 텍스트 포맷 및 레이아웃 설정
    fig_progress.update_traces(texttemplate='%{text}%', textposition='outside')
    fig_progress.update_layout(
        xaxis_title="진행률 (%)",
        yaxis_title="호선 번호",
        height=350,
        showlegend=False
    )
    
    st.plotly_chart(fig_progress, use_container_width=True)

with col_right:
    st.subheader("⚖️ 설계 중량 vs 현재 중량 비교")
    
    # 설계/현재 중량 비교를 위한 데이터 재구성 (Melt)
    df_weight = df.melt(
        id_vars=["호선"], 
        value_vars=["총_설계_중량(kg)", "현재_설치_중량(kg)"],
        var_name="구분", 
        value_name="중량(kg)"
    )
    
    fig_weight = px.bar(
        df_weight,
        x="호선",
        y="중량(kg)",
        color="구분",
        barmode="group", # 그룹형 막대 그래프
        text_auto=',.0f' # 숫자 천단위 쉼표
    )
    
    fig_weight.update_layout(
        xaxis_title="호선 번호",
        yaxis_title="중량 (kg)",
        height=350,
        legend_title_text=""
    )
    
    st.plotly_chart(fig_weight, use_container_width=True)

# ------------------------------------------------------------------
# 4. 하단 상세 데이터 테이블
# ------------------------------------------------------------------
with st.expander("📋 상세 데이터 보기"):
    st.dataframe(df, use_container_width=True)