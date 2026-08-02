import pandas as pd  # type: ignore
import streamlit as st
import plotly.express as px # type: ignore

st.set_page_config(page_title="주요 지표", layout="wide")

from src.queries import table_counts, bom_summary_by_ship

st.title("🚢 주요 지표")
st.markdown("---")
st.subheader("📋 DB테이블 및 품목 수")
df_counts = table_counts()
counts_dict = dict(zip(df_counts["table_name"], df_counts["row_count"]))
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric(label="BOM", value=f"{counts_dict.get('BOM', 0):,} 건")
with col2:
    st.metric(label="MFP", value=f"{counts_dict.get('MFP', 0):,} 건")
with col3:
    st.metric(label="INSP", value=f"{counts_dict.get('INSP', 0):,} 건")
with col4:
    st.metric(label="YDP", value=f"{counts_dict.get('YDP', 0):,} 건")


st.markdown("---")
df_summary = bom_summary_by_ship()
if isinstance(df_summary, pd.DataFrame) and not df_summary.empty:
    st.subheader("📦 BOM 호선별 집계 현황")
    df_display = df_summary[
        ["ship_no", "total_quantity", "total_weight", "total_price"]
    ]

    st.dataframe(
        df_display,
        column_config={
            "ship_no": st.column_config.TextColumn("호선 번호"),
            "total_quantity": st.column_config.NumberColumn(
                "총수량(EA)", format="%,d"
            ),
            "total_weight": st.column_config.NumberColumn(
                "총중량(kg)", format="%,.2f"
            ),
            "total_price": st.column_config.NumberColumn(
                "총금액(원)", format="%,d"
            ),
        },
        hide_index=True,
        use_container_width=True,
    )

    st.subheader("📊 BOM 호선별 비교 차트")

    c1, c2, c3 = st.columns(3)

    with c1:
        st.caption("호선별 총수량(EA)")
        st.bar_chart(
            data=df_summary,
            x="ship_no",
            y="total_quantity",
            color="#2b5c8f",
            use_container_width=True,
        )

    with c2:
        st.caption("호선별 총중량(kg)")
        st.bar_chart(
            data=df_summary,
            x="ship_no",
            y="total_weight",
            color="#2e7d32",
            use_container_width=True,
        )

    with c3:
        st.caption("호선별 총금액(원)")
        st.bar_chart(
            data=df_summary,
            x="ship_no",
            y="total_price",
            color="#c62828",
            use_container_width=True,
        )

else:
    st.info("조회된 호선 집계 데이터가 없습니다.")

st.markdown("---")


# 기존 작성하신 모듈/함수 불러오기
# (실제 프로젝트 폴더 구조에 맞게 경로 확인)
try:
    from src.queries import get_ship_summary_df  # 또는 기존에 작성하신 파일명
except ImportError:
    # 모듈을 찾지 못할 경우를 대비한 가상 함수 (테스트용)
    pass


# Page Configuration
st.set_page_config(
    page_title="호선별 공수 및 이슈 요약 대시보드",
    page_icon="🚢",
    layout="wide"
)

st.title("🚢 호선별 공수 및 이슈 요약 대시보드")
st.markdown("---")

# 데이터 로딩 함수 (캐싱 적용으로 성능 최적화)
@st.cache_data(ttl=600)
def load_data():
    return get_ship_summary_df()

try:
    with st.spinner("DB에서 데이터를 불러오는 중입니다..."):
        df = load_data()

    # Sidebar Filter
    st.sidebar.header("🔍 필터 옵션")
    
    # 제작업체 필터
    manufacturers = ['전체'] + list(df['제작업체'].dropna().unique())
    selected_mfg = st.sidebar.selectbox("제작업체 선택", manufacturers)

    # 필터링 적용
    filtered_df = df.copy()
    if selected_mfg != '전체':
        filtered_df = filtered_df[filtered_df['제작업체'] == selected_mfg]

    # 1. 상단 Key Metrics
    st.subheader("📌 주요 요약 지표")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("총 호선 수", f"{filtered_df['호선 번호'].nunique():,} 개")
    with col2:
        st.metric("총 도면 갯수", f"{filtered_df['도면 갯수'].sum():,} 개")
    with col3:
        st.metric("총 이슈 건수", f"{filtered_df['이슈 건수'].sum():,} 건")
    with col4:
        st.metric("총 공수 (M/H)", f"{filtered_df['총 공수(M/H)'].sum():,.2f}")

    st.markdown("---")

    # 2. 시각화 (시각적 전달력을 극대화하기 위한 차트)
    st.subheader("📊 호선별 총 공수 및 이슈 비교")
    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:
        fig_mh = px.bar(
            filtered_df,
            x='호선 번호',
            y='총 공수(M/H)',
            color='제작업체',
            title='호선별 총 공수 (M/H)',
            text_auto=',.0f'
        )
        st.plotly_chart(fig_mh, use_container_width=True)

    with chart_col2:
        fig_issue = px.bar(
            filtered_df,
            x='호선 번호',
            y='이슈 건수',
            color='제작업체',
            title='호선별 이슈 건수',
            text_auto=True
        )
        st.plotly_chart(fig_issue, use_container_width=True)

    # 3. 데이터 테이블
    st.subheader("📋 세부 데이터")
    st.dataframe(
        filtered_df,
        use_container_width=True,
        hide_index=True
    )

    # CSV 다운로드 버튼
    csv_data = filtered_df.to_csv(index=False).encode('utf-8-sig')
    st.download_button(
        label="📥 CSV로 데이터 다운로드",
        data=csv_data,
        file_name="ship_summary.csv",
        mime="text/csv"
    )

except Exception as e:
    st.error(f"데이터를 불러오는 중 오류가 발생했습니다: {e}")