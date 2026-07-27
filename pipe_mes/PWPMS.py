import streamlit as st

from src import queries
from src.ui import metric_row, page_title, setup_page, show_database_status, show_dataframe


setup_page("소개")

page_title(
    "배관 관리 시스템",
    "(Piping Work Process Management System)",
    "BOM / MFP",
)

show_database_status()

st.subheader("개발 목적")
st.markdown(
    """
    - 자재 관리 및 설치 공정 실시간 관리
    - 공장 별 공정 추적 관리 및 현장 작업자 역량 체크
    - 작업 시간 및 이슈(문제) 최소화
    - 불량률 최소화 직원 매달 성과급 지급
    - 현장 작업자 역량 향상과 오작, 불량률 0% 달성 실현 추구
    """
)
