import streamlit as st
# 작성하신 함수가 저장된 파일에서 불러옵니다. (파일명이 my_queries.py 라고 가정)
from src.queries import items, table_counts, table_list

# 스트림릿 웹 페이지 제목
st.title("📊 데이터베이스 현황 대시보드")

# 1. 전체 테이블 목록 보여주기
st.subheader("📋 전체 테이블 목록")
df_list = table_list()
st.dataframe(df_list, use_container_width=True)

# 2. 테이블별 데이터 건수(행 수) 보여주기
st.subheader("🔢 테이블별 레코드(행) 수")
df_counts = table_counts()
st.dataframe(df_counts, use_container_width=True)

st.set_page_config(page_title="품목 조회 대시보드", layout="wide")

st.title("📦 통합 품목(Item) 조회")

# 검색 필터 영역 (2개의 컬럼으로 나눔)
col1, col2 = st.columns([3, 1])

with col1:
    search_keyword = st.text_input(
        "🔍 검색어 (품목코드 또는 품목명)",
        placeholder="검색할 품목코드나 품목명을 입력하세요...",
    )

with col2:
    # 데이터베이스에 존재하는 item_type 종류에 맞춰 드롭다운 목록을 수정할 수 있습니다.
    type_options = ["전체", "BOM", "MFP", "INSP", "YDP"]
    selected_type = st.selectbox("🏷️ 품목 유형 선택", options=type_options)

st.divider()  # 구분선

# 3. 데이터 조회 및 출력
df = items(keyword=search_keyword.strip(), item_type=selected_type)

# 결과 수 표시 및 테이블 출력
st.subheader(f"📋 조회 결과 (총 {len(df):,}건)")

if not df.empty:
    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        # 컬럼 이름이 한글로 깔끔하게 보이도록 설정 (선택 사항)
        column_config={
            "item_id": "품목 ID",
            "item_code": "품목 코드",
            "item_name": "품목명",
            "item_type": "품목 유형",
            "unit": "단위",
            "is_active": "사용 여부",
            "lot_count": "LOT 수",
            "material_use_count": "자재 사용 수",
        },
    )
else:
    st.warning("조건에 일치하는 데이터가 없습니다.")