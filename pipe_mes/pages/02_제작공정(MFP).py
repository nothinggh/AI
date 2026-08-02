import streamlit as st
import sqlite3
import pandas as pd # type: ignore
from datetime import datetime
import re

st.set_page_config(layout="wide")

DB_PATH = "/home/gram/work/pipe_mes/sql/pipe_mes.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS MFP (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ship_no TEXT,
            dwg_type TEXT,
            dwg_no TEXT,
            lot_no TEXT,
            vendor TEXT,
            factory TEXT,
            receipt_date TEXT,
            weight REAL,
            status TEXT,
            start_time TEXT,
            end_time TEXT,
            duration REAL,
            issue_type TEXT,
            issue_desc TEXT,
            worker TEXT,
            manager TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()

def get_next_dwg_no(dwg_type):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    prefix = f"{dwg_type}-DWG-"
    c.execute("SELECT dwg_no FROM MFP WHERE dwg_no LIKE ? ORDER BY id DESC LIMIT 1", (f"{prefix}%",))
    row = c.fetchone()
    conn.close()
    if row and row[0]:
        try:
            seq = int(row[0].split("-")[-1]) + 1
        except:
            seq = 1001
    else:
        seq = 1001
    return f"{prefix}{seq}"

def get_next_lot_no(ship_no, dwg_type, vendor, dwg_no):
    """
    LOT 번호의 마지막 4자리를 도면 번호(dwg_no)의 끝 4자리 숫자와 매칭합니다.
    """
    today_str = datetime.now().strftime("%Y%m%d")
    prefix = f"{ship_no}-{dwg_type}-{vendor}-{today_str}-"
    
  
    digits = re.sub(r'\D', '', str(dwg_no))
    
    if len(digits) >= 4:
        suffix = digits[-4:] 
    elif len(digits) > 0:
        suffix = digits.zfill(4)  
    else:
        suffix = "0001"  
        
    return f"{prefix}{suffix}"


st.title("제작 공정(MFP)")
st.markdown("##### (Manufacturing Process)")
st.markdown("---")

tab_choice = st.radio("", ["1. 제작 공정 등록", "2. 제작 공정 관리"], horizontal=True)

if tab_choice == "1. 제작 공정 등록":
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        ship_no = st.text_input("호선 번호").strip().upper()
        dwg_type = st.text_input("도면 종류").strip().upper()
        
        auto_dwg = st.checkbox("도면 번호 자동 생성")
        if auto_dwg and dwg_type:
            dwg_no_val = get_next_dwg_no(dwg_type)
            dwg_no = st.text_input("도면 번호", value=dwg_no_val).upper()
        else:
            dwg_no = st.text_input("도면 번호").strip().upper()
            
        vendor = st.text_input("제작 업체명").strip().upper()
        factory = st.selectbox("배치 공장", ["공장A", "공장B", "공장C"])
        receipt_date = st.date_input("제작 도면 접수 일자")
        weight = st.number_input("중량", min_value=0.0, step=0.1)

    with col2:
        status = st.selectbox("제작 진행 상황", ["제작 중", "재 제작", "보류", "폐기", "완료", "출고"])
        start_d = st.date_input("제작 시작 날짜")
        start_t = st.time_input("제작 시작 시간")
        end_d = st.date_input("제작 완료 날짜")
        end_t = st.time_input("제작 완료 시간")
        
        start_dt = datetime.combine(start_d, start_t)
        end_dt = datetime.combine(end_d, end_t)
        
        if end_dt >= start_dt:
            duration = round((end_dt - start_dt).total_seconds() / 3600.0, 2)
        else:
            duration = 0.0
            
        st.number_input("실 투입 시간 (시간 단위 자동계산)", value=duration, disabled=True)

    with col3:
        issue_type = st.selectbox("제작 문제", ["없음", "파손", "불량", "오작"])
        issue_desc = st.text_area("이슈").strip().upper()
        worker = st.text_input("작업자").strip().upper()
        manager = st.text_input("관리자").strip().upper()
        
        auto_lot = st.checkbox("LOT 제작 번호 자동 생성", value=True)
        
        if auto_lot and ship_no and dwg_type and vendor and dwg_no:
            generated_lot = get_next_lot_no(ship_no, dwg_type, vendor, dwg_no)
            lot_no = st.text_input("LOT 제작 번호", value=generated_lot, disabled=True)
        else:
            lot_no = st.text_input("LOT 제작 번호").strip().upper()

    if st.button("등록하기", use_container_width=True):
        if not ship_no or not dwg_type or not dwg_no or not vendor:
            st.error("필수 항목(호선 번호, 도면 종류, 도면 번호, 제작 업체명)을 입력하세요.")
        else:
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            c.execute("""
                INSERT INTO MFP (
                    ship_no, dwg_type, dwg_no, lot_no, vendor, factory, receipt_date, weight,
                    status, start_time, end_time, duration, issue_type, issue_desc, worker, manager
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                ship_no, dwg_type, dwg_no, lot_no, vendor, factory, str(receipt_date), weight,
                status, str(start_dt), str(end_dt), duration, issue_type, issue_desc, worker, manager
            ))
            conn.commit()
            conn.close()
            st.success("성공적으로 등록되었습니다.")

elif tab_choice == "2. 제작 공정 관리":
    
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM MFP", conn)
    conn.close()

    col_s1, col_s2 = st.columns([1, 3])
    with col_s1:
        search_col = st.selectbox("검색 컬럼", ["전체"] + list(df.columns))
    with col_s2:
        search_keyword = st.text_input("검색어").strip().upper()

    if search_keyword:
        if search_col == "전체":
            mask = df.astype(str).apply(lambda row: row.str.contains(search_keyword, case=False).any(), axis=1)
            filtered_df = df[mask]
        else:
            filtered_df = df[df[search_col].astype(str).str.contains(search_keyword, case=False, na=False)]
    else:
        filtered_df = df.copy()

    if not filtered_df.empty:
        select_all = st.checkbox("전체 선택 / 해제")
        filtered_df.insert(0, "선택", select_all)

        edited_df = st.data_editor(
            filtered_df,
            column_config={
                "id": st.column_config.NumberColumn("id", disabled=True),
                "factory": st.column_config.SelectboxColumn("factory", options=["공장A", "공장B", "공장C"]),
                "status": st.column_config.SelectboxColumn("status", options=["제작 중", "재 제작", "보류", "폐기", "완료", "출고"]),
                "issue_type": st.column_config.SelectboxColumn("issue_type", options=["없음", "파손", "불량", "오작"])
            },
            hide_index=True,
            use_container_width=True
        )

        btn_col1, btn_col2 = st.columns(2)
        
        with btn_col1:
            if st.button("선택 항목 수정 저장", use_container_width=True):
                selected_rows = edited_df[edited_df["선택"] == True]
                if selected_rows.empty:
                    st.warning("수정할 항목을 선택하세요.")
                else:
                    conn = sqlite3.connect(DB_PATH)
                    c = conn.cursor()
                    for idx, row in selected_rows.iterrows():
                        c.execute("""
                            UPDATE MFP SET
                                ship_no=?, dwg_type=?, dwg_no=?, lot_no=?, vendor=?, factory=?,
                                receipt_date=?, weight=?, status=?, start_time=?, end_time=?,
                                duration=?, issue_type=?, issue_desc=?, worker=?, manager=?
                            WHERE id=?
                        """, (
                            str(row['ship_no']).upper(), str(row['dwg_type']).upper(), str(row['dwg_no']).upper(),
                            str(row['lot_no']).upper(), str(row['vendor']).upper(), str(row['factory']),
                            str(row['receipt_date']), row['weight'], str(row['status']),
                            str(row['start_time']), str(row['end_time']), row['duration'],
                            str(row['issue_type']), str(row['issue_desc']).upper(),
                            str(row['worker']).upper(), str(row['manager']).upper(),
                            row['id']
                        ))
                    conn.commit()
                    conn.close()
                    st.success("수정 사항이 저장되었습니다.")
                    st.rerun()

        with btn_col2:
            if st.button("선택 항목 삭제", use_container_width=True):
                selected_rows = edited_df[edited_df["선택"] == True]
                if selected_rows.empty:
                    st.warning("삭제할 항목을 선택하세요.")
                else:
                    conn = sqlite3.connect(DB_PATH)
                    c = conn.cursor()
                    for idx, row in selected_rows.iterrows():
                        c.execute("DELETE FROM MFP WHERE id=?", (row['id'],))
                    conn.commit()
                    conn.close()
                    st.success("선택한 항목이 삭제되었습니다.")
                    st.rerun()
    else:
        st.info("조회된 데이터가 없습니다.")