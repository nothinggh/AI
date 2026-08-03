import streamlit as st

from src.ui import (
    page_title,
    setup_page,
    show_database_status,
)

st.set_page_config(layout="wide")

setup_page("소개")

page_title(
    "배관 관리 시스템",
    "(Piping Manufacturing Execution System)",
    "BOM MFP INSP YDP",
)

show_database_status()

st.subheader("개발 목적")
st.markdown("""
    - 자재 관리 및 설치 공정 실시간 관리
    - 공장 별 공정 추적 관리 및 현장 작업자 역량 체크
    - 작업 시간 및 이슈(문제) 최소화
    - 불량률 최소화 직원 매달 성과급 지급
    - 현장 작업자 역량 향상과 오작, 불량률 0% 달성 실현 추구
    """)


st.markdown("""
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
<style>
    .step-card {
        background-color: #ffffff;
        border: 2px solid #e0e0e0;
        border-radius: 12px;
        padding: 24px 16px;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        transition: transform 0.2s, border-color 0.2s;
        height: 100%;
    }
    .step-card:hover {
        transform: translateY(-4px);
        border-color: #1E88E5;
        box-shadow: 0 8px 15px rgba(30,136,229,0.15);
    }
    .step-badge {
        background-color: #1E88E5;
        color: white;
        font-weight: bold;
        font-size: 14px;
        padding: 4px 12px;
        border-radius: 20px;
        display: inline-block;
        margin-bottom: 12px;
    }
    .step-icon {
        font-size: 52px; /* 아이콘 크기 확대 */
        color: #2C3E50;
        margin: 16px 0;
    }
    .step-title {
        font-size: 18px;
        font-weight: 700;
        color: #1A252C;
        margin-bottom: 8px;
    }
    .step-desc {
        font-size: 14px;
        color: #555555;
        word-break: keep-all;
    }
    .arrow-container {
        display: flex;
        align-items: center;
        justify-content: center;
        height: 100%;
        color: #90A4AE;
        font-size: 28px;
    }
</style>
""", unsafe_allow_html=True)


st.markdown("---")
st.subheader("배관 작업 순서(Piping Work Procedure)")


steps = [
    {
        "code": "STEP 1",
        "name": "BOM",
        "desc": "자재 구매",
        "icon": "fa-solid fa-boxes-packing"
    },
    {
        "code": "STEP 2",
        "name": "MFP",
        "desc": "배관 제작",
        "icon": "fa-solid fa-industry"
    },
    {
        "code": "STEP 3",
        "name": "INSP",
        "desc": "개별 배관 GROUP화 진행",
        "icon": "fa-solid fa-object-group"
    },
    {
        "code": "STEP 4",
        "name": "YDP",
        "desc": "GROUP화 배관 조선소 현장 설치",
        "icon": "fa-solid fa-ship"
    }
]


cols = st.columns([3, 1, 3, 1, 3, 1, 3])

for idx, step in enumerate(steps):
    
    col_idx = idx * 2
    with cols[col_idx]:
        st.markdown(f"""
            <div class="step-card">
                <div class="step-badge">{step['code']}</div>
                <div class="step-icon"><i class="{step['icon']}"></i></div>
                <div class="step-title">{step['name']}</div>
                <div class="step-desc">{step['desc']}</div>
            </div>
        """, unsafe_allow_html=True)
    
    
    if idx < len(steps) - 1:
        with cols[col_idx + 1]:
            st.markdown("""
                <div class="arrow-container">
                    <i class="fa-solid fa-chevron-right"></i>
                </div>
            """, unsafe_allow_html=True)

st.markdown("<br><br>", unsafe_allow_html=True)


with st.expander("각 단계별 상세 설명 보기"):
    st.markdown("""
    - **1. BOM (Bill of Materials):** 필요 자재 산출 및 구매 발주 진행 단계
    - **2. MFP (Manufacturing Process):** 자재 절단, 벤딩 및 개별 배관 제작 단계
    - **3. INSP (Installation Process):** 효율적 설치를 위한 배관 Grouping
    - **4. YDP (Yard Delivery Process):** 조선소 품질 검사, Block 설치 및 Dock 최종 탑재
    """)

