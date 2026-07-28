import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime, time

st.set_page_config(layout="wide")

DB_PATH = "/home/gram/work/pipe_mes/sql/pipe_mes.db"

def get_connection():
    return sqlite3.connect(DB_PATH)

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS YDP (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            lot_no TEXT,
            ship_no TEXT,
            unit_no TEXT,
            weight REAL,
            block_no TEXT,
            area TEXT,
            inspection TEXT,
            status TEXT,
            start_datetime TEXT,
            end_datetime TEXT,
            duration TEXT,
            workers INTEGER,
            manager TEXT,
            issue TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()

st.title("Yard 공정(YDP)")
st.markdown("##### (Yard Process)")
st.markdown("---")

tab = st.radio("메뉴 선택", ["1. Yard 공정 등록", "2. Yard 공정 관리"], horizontal=True)

if tab == "1. Yard 공정 등록":
    col1, col2 = st.columns(2)
    
    with col1:
        ship_no = st.text_input("호선 번호").upper()
        unit_no = st.selectbox("UNIT NO", ["UNIT-A", "UNIT-B", "UNIT-C", "UNIT-D", "UNIT-E", "UNIT-F", "UNIT-G", "UNIT-H", "UNIT-I", "UNIT-J"])
        weight = st.number_input("중량", min_value=0.0, step=0.1)
        block_no = st.selectbox("BLOCK NO", [f"B10{i}" for i in range(1, 10)] + ["B110"])
        area = st.selectbox("AREA", ["E/R(엔진룸)", "HULL(선장)", "C/R(선실)"])
        inspection = st.selectbox("검사", ["통과", "용접 검사", "수압 검사", "기밀 검사"])
        status = st.selectbox("YARD 진행 상황", ["검사", "보류", "소조립", "중조립", "대조립", "DOCK 탑재", "시운전", "인도"])
    
    with col2:
        lot_no = f"{ship_no}-INST-{block_no}" if ship_no else ""
        st.text_input("LOT NO (자동 생성)", value=lot_no, disabled=True)
        
        c1, c2 = st.columns(2)
        with c1:
            start_date = st.date_input("YARD 시작 날짜")
            start_time = st.time_input("YARD 시작 시간", value=time(9, 0))
        with c2:
            end_date = st.date_input("YARD 완료 날짜")
            end_time = st.time_input("YARD 완료 시간", value=time(18, 0))
            
        start_dt = datetime.combine(start_date, start_time)
        end_dt = datetime.combine(end_date, end_time)
        
        duration_str = ""
        if end_dt >= start_dt:
            diff = end_dt - start_dt
            hours, remainder = divmod(diff.total_seconds(), 3600)
            minutes = remainder // 60
            duration_str = f"{int(hours)}시간 {int(minutes)}분"
        else:
            duration_str = "종료 시간이 시작 시간보다 빠릅니다"
            
        st.text_input("YARD 걸린 실 투입 시간", value=duration_str, disabled=True)
        
        workers = st.number_input("YARD 투입 인원", min_value=0, step=1)
        manager = st.text_input("YARD 관리자").upper()
        issue = st.text_area("이슈").upper()

    if st.button("등록", use_container_width=True):
        if not ship_no or not manager:
            st.error("호선 번호와 관리자를 입력해주세요.")
        elif end_dt < start_dt:
            st.error("완료 시간이 시작 시간보다 빠를 수 없습니다.")
        else:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO YDP (lot_no, ship_no, unit_no, weight, block_no, area, inspection, status, start_datetime, end_datetime, duration, workers, manager, issue)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                lot_no, ship_no, unit_no, weight, block_no, area, inspection, status,
                start_dt.strftime("%Y-%m-%d %H:%M"), end_dt.strftime("%Y-%m-%d %H:%M"),
                duration_str, workers, manager, issue
            ))
            conn.commit()
            conn.close()
            st.success("등록되었습니다.")

elif tab == "2. Yard 공정 관리":
    conn = get_connection()
    df = pd.read_sql("SELECT * FROM YDP", conn)
    conn.close()

    st.subheader("조회 및 검색")
    c_search1, c_search2 = st.columns([1, 3])
    
    with c_search1:
        search_col = st.selectbox("검색 컬럼", ["전체"] + list(df.columns))
    with c_search2:
        search_keyword = st.text_input("검색어 입력").upper()

    if search_keyword:
        if search_col == "전체":
            mask = df.astype(str).apply(lambda row: row.str.contains(search_keyword, case=False).any(), axis=1)
            df = df[mask]
        else:
            df = df[df[search_col].astype(str).str.contains(search_keyword, case=False, na=False)]

    if not df.empty:
        c_btn1, c_btn2 = st.columns([1, 8])
        with c_btn1:
            select_all = st.checkbox("전체 선택")

        df.insert(0, "선택", select_all)

        unit_opts = ["UNIT-A", "UNIT-B", "UNIT-C", "UNIT-D", "UNIT-E", "UNIT-F", "UNIT-G", "UNIT-H", "UNIT-I", "UNIT-J"]
        block_opts = [f"B10{i}" for i in range(1, 10)] + ["B110"]
        area_opts = ["E/R(엔진룸)", "HULL(선장)", "C/R(선실)"]
        insp_opts = ["통과", "용접 검사", "수압 검사", "기밀 검사"]
        status_opts = ["검사", "보류", "소조립", "중조립", "대조립", "DOCK 탑재", "시운전", "인도"]

        edited_df = st.data_editor(
            df,
            column_config={
                "선택": st.column_config.CheckboxColumn("선택", default=False),
                "id": st.column_config.NumberColumn("ID", disabled=True),
                "lot_no": st.column_config.TextColumn("LOT NO", disabled=True),
                "ship_no": st.column_config.TextColumn("호선 번호"),
                "unit_no": st.column_config.SelectboxColumn("UNIT NO", options=unit_opts),
                "weight": st.column_config.NumberColumn("중량"),
                "block_no": st.column_config.SelectboxColumn("BLOCK NO", options=block_opts),
                "area": st.column_config.SelectboxColumn("AREA", options=area_opts),
                "inspection": st.column_config.SelectboxColumn("검사", options=insp_opts),
                "status": st.column_config.SelectboxColumn("진행 상황", options=status_opts),
                "start_datetime": st.column_config.TextColumn("시작 일시 (YYYY-MM-DD HH:MM)"),
                "end_datetime": st.column_config.TextColumn("완료 일시 (YYYY-MM-DD HH:MM)"),
                "duration": st.column_config.TextColumn("투입 시간"),
                "workers": st.column_config.NumberColumn("투입 인원"),
                "manager": st.column_config.TextColumn("관리자"),
                "issue": st.column_config.TextColumn("이슈")
            },
            hide_index=True,
            use_container_width=True,
            num_rows="fixed"
        )

        col_act1, col_act2 = st.columns(2)
        
        with col_act1:
            if st.button("선택 항목 수정 저장", use_container_width=True):
                selected_rows = edited_df[edited_df["선택"] == True]
                if selected_rows.empty:
                    st.warning("수정할 항목을 선택해주세요.")
                else:
                    conn = get_connection()
                    cursor = conn.cursor()
                    for idx, row in selected_rows.iterrows():
                        u_ship = str(row['ship_no']).upper()
                        u_block = str(row['block_no']).upper()
                        u_lot = f"{u_ship}-INST-{u_block}"
                        u_manager = str(row['manager']).upper()
                        u_issue = str(row['issue']).upper() if pd.notna(row['issue']) else ""
                        
                        try:
                            s_dt = datetime.strptime(str(row['start_datetime']), "%Y-%m-%d %H:%M")
                            e_dt = datetime.strptime(str(row['end_datetime']), "%Y-%m-%d %H:%M")
                            if e_dt >= s_dt:
                                diff = e_dt - s_dt
                                h, r = divmod(diff.total_seconds(), 3600)
                                m = r // 60
                                u_duration = f"{int(h)}시간 {int(m)}분"
                            else:
                                u_duration = "오류"
                        except:
                            u_duration = str(row['duration'])

                        cursor.execute("""
                            UPDATE YDP SET 
                                lot_no=?, ship_no=?, unit_no=?, weight=?, block_no=?, area=?, 
                                inspection=?, status=?, start_datetime=?, end_datetime=?, 
                                duration=?, workers=?, manager=?, issue=?
                            WHERE id=?
                        """, (
                            u_lot, u_ship, row['unit_no'], row['weight'], u_block, row['area'],
                            row['inspection'], row['status'], str(row['start_datetime']), str(row['end_datetime']),
                            u_duration, row['workers'], u_manager, u_issue, row['id']
                        ))
                    conn.commit()
                    conn.close()
                    st.success("선택한 항목이 수정되었습니다.")
                    st.rerun()

        with col_act2:
            if st.button("선택 항목 삭제", use_container_width=True):
                selected_rows = edited_df[edited_df["선택"] == True]
                if selected_rows.empty:
                    st.warning("삭제할 항목을 선택해주세요.")
                else:
                    conn = get_connection()
                    cursor = conn.cursor()
                    ids_to_delete = selected_rows["id"].tolist()
                    cursor.executemany("DELETE FROM YDP WHERE id=?", [(i,) for i in ids_to_delete])
                    conn.commit()
                    conn.close()
                    st.success("선택한 항목이 삭제되었습니다.")
                    st.rerun()
    else:
        st.info("조회된 데이터가 없습니다.")