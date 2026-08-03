import sqlite3
import pandas as pd # type: ignore
import streamlit as st
from datetime import datetime, time

st.set_page_config(layout="wide")

DB_PATH = "/home/gram/work/pipe_mes/sql/pipe_mes.db"

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS YDP (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            lot_no TEXT,
            ship_no TEXT,
            block_no TEXT,
            unit_no TEXT,
            area TEXT,
            inspection TEXT,
            progress TEXT,
            start_datetime TEXT,
            end_datetime TEXT,
            actual_hours REAL,
            headcount INTEGER,
            manager TEXT,
            issue TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()


st.title("🏗️ YARD 공정(YDP)")
st.markdown("##### (Yard Delivery Process)")
st.markdown("---")

menu = st.radio("", ["1. YARD 공정 등록", "2. YARD 공정 관리"], horizontal=True)

if menu == "1. YARD 공정 등록":
   
    col1, col2, col3 = st.columns(3)
    
    with col1:
        ship_no = st.text_input("호선 번호").upper()
        block_options = [f"B10{i}" if i < 10 else f"B1{i}" for i in range(1, 11)]
        block_no = st.selectbox("block no", block_options)
        unit_options = [f"UNIT-{chr(i)}" for i in range(65, 75)]
        unit_no = st.selectbox("unit no", unit_options)
        area = st.selectbox("area", ["E/R(엔진룸)", "HULL(선장)", "C/R(선실)"])
        inspection = st.selectbox("검사", ["완료", "용접,수압,기밀"])
        
    with col2:
        progress = st.selectbox("yard 진행 상황", ["검사", "보류", "소조립", "중조립", "대조립", "DOCK 탑재", "시운전", "인도"])
        start_date = st.date_input("yard 시작 날짜")
        start_time_val = st.time_input("yard 시작 시간", value=time(9, 0))
        end_date = st.date_input("yard 완료 날짜")
        end_time_val = st.time_input("yard 완료 시간", value=time(18, 0))
        
    with col3:
        start_dt = datetime.combine(start_date, start_time_val)
        end_dt = datetime.combine(end_date, end_time_val)
        
        time_diff = end_dt - start_dt
        actual_hours = round(time_diff.total_seconds() / 3600, 2)
        if actual_hours < 0:
            actual_hours = 0.0
            
        st.number_input("yard 실 투입 시간(시간)", value=actual_hours, disabled=True)
        headcount = st.number_input("yard 투입 인원", min_value=0, step=1)
        manager = st.text_input("yard 관리자").upper()
        issue = st.text_area("이슈").upper()

    lot_no = f"{ship_no}-YARD-{block_no}".upper() if ship_no else ""
    st.text_input("lot no (자동 생성)", value=lot_no, disabled=True)

    if st.button("등록"):
        if not ship_no:
            st.error("호선 번호를 입력하세요.")
        else:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO YDP (
                    lot_no, ship_no, block_no, unit_no, area, inspection, progress,
                    start_datetime, end_datetime, actual_hours, headcount, manager, issue
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                lot_no, ship_no, block_no, unit_no, area, inspection, progress,
                start_dt.strftime("%Y-%m-%d %H:%M:%S"),
                end_dt.strftime("%Y-%m-%d %H:%M:%S"),
                actual_hours, headcount, manager, issue
            ))
            conn.commit()
            conn.close()
            st.success("등록되었습니다.")

elif menu == "2. YARD 공정 관리":
    
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM YDP", conn)
    conn.close()
    
    s_col1, s_col2 = st.columns([1, 2])
    
    columns_list = ["전체"] + list(df.columns) if not df.empty else ["전체"]
    with s_col1:
        search_col = st.selectbox("검색 컬럼", columns_list)
    with s_col2:
        search_kw = st.text_input("검색어").upper()

    filtered_df = df.copy()
    if search_kw and not df.empty:
        if search_col == "전체":
            mask = df.astype(str).apply(lambda row: row.str.contains(search_kw, case=False).any(), axis=1)
            filtered_df = df[mask]
        else:
            filtered_df = df[df[search_col].astype(str).str.contains(search_kw, case=False, na=False)]

    
    col_btn1, col_btn2 = st.columns([1, 10])
    with col_btn1:
        select_all = st.checkbox("전체 선택")

    if not filtered_df.empty:
        filtered_df.insert(0, "선택", select_all)
        
        column_config = {
            "선택": st.column_config.CheckboxColumn("선택", default=False),
            "id": st.column_config.NumberColumn("id", disabled=True),
            "lot_no": st.column_config.TextColumn("lot_no", disabled=True),
            "block_no": st.column_config.SelectboxColumn("block_no", options=[f"B10{i}" if i < 10 else f"B1{i}" for i in range(1, 11)]),
            "unit_no": st.column_config.SelectboxColumn("unit_no", options=[f"UNIT-{chr(i)}" for i in range(65, 75)]),
            "area": st.column_config.SelectboxColumn("area", options=["E/R(엔진룸)", "HULL(선장)", "C/R(선실)"]),
            "inspection": st.column_config.SelectboxColumn("inspection", options=["완료", "용접,수압,기밀"]),
            "progress": st.column_config.SelectboxColumn("progress", options=["검사", "보류", "소조립", "중조립", "대조립", "DOCK 탑재", "시운전", "인도"])
        }

        edited_df = st.data_editor(
            filtered_df,
            column_config=column_config,
            hide_index=True,
            use_container_width=True,
            num_rows="fixed"
        )

        col_act1, col_act2 = st.columns([1, 10])
        
        with col_act1:
            if st.button("수정 저장"):
                conn = get_connection()
                cursor = conn.cursor()
                for idx, row in edited_df.iterrows():
                    ship_val = str(row["ship_no"]).upper() if row["ship_no"] else ""
                    block_val = str(row["block_no"])
                    lot_val = f"{ship_val}-YARD-{block_val}"
                    
                    try:
                        s_dt = datetime.strptime(str(row["start_datetime"]), "%Y-%m-%d %H:%M:%S")
                        e_dt = datetime.strptime(str(row["end_datetime"]), "%Y-%m-%d %H:%M:%S")
                        act_hrs = round((e_dt - s_dt).total_seconds() / 3600, 2)
                        if act_hrs < 0:
                            act_hrs = 0.0
                    except:
                        act_hrs = row["actual_hours"]

                    cursor.execute("""
                        UPDATE YDP SET
                            lot_no = ?,
                            ship_no = ?,
                            block_no = ?,
                            unit_no = ?,
                            area = ?,
                            inspection = ?,
                            progress = ?,
                            start_datetime = ?,
                            end_datetime = ?,
                            actual_hours = ?,
                            headcount = ?,
                            manager = ?,
                            issue = ?
                        WHERE id = ?
                    """, (
                        lot_val,
                        ship_val,
                        block_val,
                        row["unit_no"],
                        row["area"],
                        row["inspection"],
                        row["progress"],
                        str(row["start_datetime"]),
                        str(row["end_datetime"]),
                        act_hrs,
                        row["headcount"],
                        str(row["manager"]).upper() if row["manager"] else "",
                        str(row["issue"]).upper() if row["issue"] else "",
                        row["id"]
                    ))
                conn.commit()
                conn.close()
                st.success("수정사항이 저장되었습니다.")
                st.rerun()

        with col_act2:
            if st.button("선택 삭제"):
                selected_ids = edited_df[edited_df["선택"] == True]["id"].tolist()
                if selected_ids:
                    conn = get_connection()
                    cursor = conn.cursor()
                    cursor.executemany("DELETE FROM YDP WHERE id = ?", [(i,) for i in selected_ids])
                    conn.commit()
                    conn.close()
                    st.success("선택한 항목이 삭제되었습니다.")
                    st.rerun()
                else:
                    st.warning("삭제할 항목을 선택하세요.")
    else:
        st.info("조회된 데이터가 없습니다.")