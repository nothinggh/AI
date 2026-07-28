import sqlite3
import pandas as pd
import streamlit as st

# 1. DB 경로 설정
DB_PATH = "/home/gram/work/pipe_mes/sql/pipe_mes.db"

# 2. SQLite 데이터베이스 연결 및 쿼리 실행 함수
def get_total_weight(ship_no):
    try:
        conn = sqlite3.connect(DB_PATH)
        
        # ------------------------------------------------------------------
        #  SQL 쿼리문
        # - BOM 테이블에서 호선 번호가 'sn101'인 데이터의 weight(중량) 합계 구하기
        # - ※ 실제 DB의 컬럼명(ship_no, weight 등)에 맞춰 수정해 주세요.
        # ------------------------------------------------------------------
        query = """
        SELECT 
            SUM(weight) AS total_weight 
        FROM BOM 
        WHERE ship_no = ?
        """
        
        # SQL 실행 및 결과 가져오기
        df = pd.read_sql_query(query, conn, params=(ship_no,))
        conn.close()
        
        # 합계 결과값 추출 (결과가 없거나 NULL이면 0 처리)
        total_weight = df['total_weight'].iloc[0]
        return total_weight if pd.notnull(total_weight) else 0

    except Exception as e:
        st.error(f"DB 조회 중 에러 발생: {e}")
        return None

# --- Streamlit UI 구현 ---
st.title("🚢 호선별 총 중량 조회")

target_ship = "sn101"
total_w = get_total_weight(target_ship)

if total_w is not None:
    # 1) 메트릭 카드로 깔끔하게 표시 (추천)
    st.metric(
        label=f"호선 번호: {target_ship} 총 중량", 
        value=f"{total_w:,.2f} kg"  # 천 단위 쉼표 + 소수점 둘째자리 포맷팅
    )

    # 2) 단순 텍스트/알림 창 형태로 표시
    st.success(f"**{target_ship}** 호선의 전체 중량 합계는 **{total_w:,.2f} kg** 입니다.")