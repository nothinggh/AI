import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime, timedelta

DB_PATH = "/home/gram/work/pipe_mes/sql/pipe_mes.db"

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS INSP (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            lot_no TEXT,
            ship_no TEXT,
            dwg_no TEXT,
            unit_no TEXT,
            dwg_receipt_date TEXT,
            status TEXT,
            start_time TEXT,
            end_time TEXT,
            duration_hours REAL,
            vendor TEXT,
            headcount INTEGER,
            manager TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()

st.set_page_config(layout="wide")

st.markdown("---")
st.title("설치 공정(INSP)")
st.markdown("##### (Installation Process)")
st.markdown("---")

tab_choice = st.radio("", ["1. 설치 공정 등록", "2. 설치 공정 관리"], horizontal=True)

if tab_choice == "1. 설치 공정 등록":
    st.subheader("1. 설치 공정 등록")
    
    with st.form("register_form"):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            ship_no = st.text_input("호선 번호").strip().upper()
            dwg_no = st.text_input("dwg no").strip().upper()
            unit_no = st.selectbox("unit no", ["UNIT-A", "UNIT-B", "UNIT-C", "UNIT-D", "UNIT-E", "UNIT-F", "UNIT-G", "UNIT-H", "UNIT-I", "UNIT-J"])
            user_lot_input = st.text_input("LOT 사용자 입력").strip().upper()
            
        with col2:
            dwg_receipt_date = st.date_input("설치 도면 접수 일자")
            status = st.selectbox("설치 진행 상황", ["설치 중", "보류", "완료", "출고"])
            start_date = st.date_input("설치 시작 날짜", datetime.now())
            start_time_val = st.time_input("설치 시작 시간", datetime.now().time())
            
        with col3:
            end_date = st.date_input("설치 완료 날짜", datetime.now())
            end_time_val = st.time_input("설치 완료 시간", datetime.now().time())
            vendor = st.selectbox("설치 업체", ["AA", "BB", "CC"])
            headcount = st.number_input("설치 투입 인원", min_value=0, step=1)
            manager = st.text_input("설치 관리자").strip().upper()

        start_dt = datetime.combine(start_date, start_time_val)
        end_dt = datetime.combine(end_date, end_time_val)
        
        duration = 0.0
        if end_dt > start_dt:
            duration = round((end_dt - start_dt).total_seconds() / 3600.0, 2)
            
        st.info(f"계산된 실 투입 시간: {duration} 시간")

        submitted = st.form_submit_button("등록")
        
        if submitted:
            lot_no = f"{ship_no}-INST-{unit_no}-{user_lot_input}"
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO INSP (
                    lot_no, ship_no, dwg_no, unit_no, dwg_receipt_date, 
                    status, start_time, end_time, duration_hours, 
                    vendor, headcount, manager
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                lot_no, ship_no, dwg_no, unit_no, str(dwg_receipt_date),
                status, start_dt.strftime("%Y-%m-%d %H:%M"), end_dt.strftime("%Y-%m-%d %H:%M"),
                duration, vendor, headcount, manager
            ))
            conn.commit()
            conn.close()
            st.success("등록되었습니다.")

elif tab_choice == "2. 설치 공정 관리":
    st.subheader("2. 설치 공정 관리")

    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM INSP", conn)
    conn.close()

    if not df.empty:
        st.markdown("##### 검색조건")
        sc1, sc2 = st.columns([1, 3])
        with sc1:
            search_col = st.selectbox("검색 항목", ["전체"] + list(df.columns))
        with sc2:
            search_kw = st.text_input("검색어").strip()

        filtered_df = df.copy()
        if search_kw:
            if search_col == "전체":
                mask = filtered_df.astype(str).apply(lambda x: x.str.contains(search_kw, case=False)).any(axis=1)
                filtered_df = filtered_df[mask]
            else:
                filtered_df = filtered_df[filtered_df[search_col].astype(str).str.contains(search_kw, case=False)]

        select_all = st.checkbox("전체 선택 / 해제")
        
        if "select_all" not in st.session_state:
            st.session_state["select_all"] = False
            
        if select_all != st.session_state["select_all"]:
            st.session_state["select_all"] = select_all
            for idx in filtered_df.index:
                st.session_state[f"chk_{filtered_df.loc[idx, 'id']}"] = select_all

        edited_df = st.data_editor(
            filtered_df,
            column_config={
                "id": st.column_config.NumberColumn("ID", disabled=True),
                "unit_no": st.column_config.SelectboxColumn("UNIT NO", options=["UNIT-A", "UNIT-B", "UNIT-C", "UNIT-D", "UNIT-E", "UNIT-F", "UNIT-G", "UNIT-H", "UNIT-I", "UNIT-J"]),
                "status": st.column_config.SelectboxColumn("진행 상황", options=["설치 중", "보류", "완료", "출고"]),
                "vendor": st.column_config.SelectboxColumn("업체", options=["AA", "BB", "CC"]),
            },
            use_container_width=True,
            num_rows="dynamic",
            key="editor"
        )

        col_btn1, col_btn2 = st.columns([1, 10])
        with col_btn1:
            if st.button("수정 내용 저장"):
                conn = get_connection()
                cursor = conn.cursor()
                for idx, row in edited_df.iterrows():
                    for col in edited_df.columns:
                        if isinstance(row[col], str):
                            row[col] = row[col].upper()
                            
                    cursor.execute("""
                        UPDATE INSP SET
                            lot_no = ?,
                            ship_no = ?,
                            dwg_no = ?,
                            unit_no = ?,
                            dwg_receipt_date = ?,
                            status = ?,
                            start_time = ?,
                            end_time = ?,
                            duration_hours = ?,
                            vendor = ?,
                            headcount = ?,
                            manager = ?
                        WHERE id = ?
                    """, (
                        row["lot_no"], row["ship_no"], row["dwg_no"], row["unit_no"],
                        row["dwg_receipt_date"], row["status"], row["start_time"],
                        row["end_time"], row["duration_hours"], row["vendor"],
                        row["headcount"], row["manager"], row["id"]
                    ))
                conn.commit()
                conn.close()
                st.success("저장되었습니다.")
                st.rerun()

        if st.session_state.get("editor"):
            deleted_rows = st.session_state["editor"].get("deleted_rows", [])
            if deleted_rows:
                conn = get_connection()
                cursor = conn.cursor()
                for r_idx in deleted_rows:
                    target_id = filtered_df.iloc[r_idx]["id"]
                    cursor.execute("DELETE FROM INSP WHERE id = ?", (target_id,))
                conn.commit()
                conn.close()
                st.success("삭제되었습니다.")
                st.rerun()
    else:
        st.info("조회할 데이터가 없습니다.")