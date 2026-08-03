from datetime import datetime
import sqlite3
import pandas as pd # type: ignore
import streamlit as st

st.set_page_config(layout="wide")

DB_PATH = "/home/gram/work/pipe_mes/sql/pipe_mes.db"


def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute(
        """
        CREATE TABLE IF NOT EXISTS INSP (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            lot_no TEXT,
            ship_no TEXT,
            dwg_no TEXT,
            unit_no TEXT,
            weight REAL,
            receipt_date TEXT,
            status TEXT,
            start_time TEXT,
            end_time TEXT,
            duration REAL,
            vendor TEXT,
            workers INTEGER,
            manager TEXT,
            issue TEXT
        )
    """
    )

    c.execute("PRAGMA table_info(INSP)")
    columns = [col[1] for col in c.fetchall()]
    if "issue" not in columns:
        c.execute("ALTER TABLE INSP ADD COLUMN issue TEXT")

    conn.commit()
    conn.close()


init_db()


st.title("🔩 설치 공정(INSP)")
st.markdown("##### (Installation Process)")
st.markdown("---")

tab = st.radio(
    "메뉴 선택",
    ["1. 설치 공정 등록", "2. 설치 공정 관리"],
    horizontal=True,
    label_visibility="collapsed",
)

if tab == "1. 설치 공정 등록":
   
    with st.form("register_form"):
        col1, col2, col3 = st.columns(3)

        with col1:
            ship_no = st.text_input("호선 번호").upper()
            dwg_no = st.text_input("dwg no").upper()
            unit_options = [
                "UNIT-A",
                "UNIT-B",
                "UNIT-C",
                "UNIT-D",
                "UNIT-E",
                "UNIT-F",
                "UNIT-G",
                "UNIT-H",
                "UNIT-I",
                "UNIT-J",
            ]
            unit_no = st.selectbox("unit no", unit_options)
            weight = st.number_input("중량", min_value=0.0, step=0.1)

        with col2:
            receipt_date = st.date_input("설치 도면 접수 일자")
            status_options = ["설치 중", "보류", "파손", "완료", "출고"]
            status = st.selectbox("설치 진행 상황", status_options)
            start_date = st.date_input("설치 시작 날짜")
            start_time = st.time_input("설치 시작 시간")
            end_date = st.date_input("설치 완료 날짜")
            end_time = st.time_input("설치 완료 시간")

        with col3:
            vendor_options = ["AA", "BB", "CC"]
            vendor = st.selectbox("설치 업체", vendor_options)
            workers = st.number_input("설치 투입 인원", min_value=0, step=1)
            manager = st.text_input("설치 관리자").upper()

            lot_no = f"{ship_no}-INST-{unit_no}"
            st.text_input("lot no", value=lot_no, disabled=True)

            start_dt = datetime.combine(start_date, start_time)
            end_dt = datetime.combine(end_date, end_time)
            duration = round((end_dt - start_dt).total_seconds() / 3600, 2)
            st.number_input(
                "설치 시 걸린 실 투입 시간(시간)", value=duration, disabled=True
            )

        issue = st.text_area("이슈", placeholder="특이사항이나 문제 발생 원인/내용을 입력하세요.")

        submitted = st.form_submit_button("등록")

        if submitted:
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            c.execute(
                """
                INSERT INTO INSP (
                    lot_no, ship_no, dwg_no, unit_no, weight, 
                    receipt_date, status, start_time, end_time, 
                    duration, vendor, workers, manager, issue
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    lot_no,
                    ship_no,
                    dwg_no,
                    unit_no,
                    weight,
                    receipt_date.strftime("%Y-%m-%d"),
                    status,
                    start_dt.strftime("%Y-%m-%d %H:%M:%S"),
                    end_dt.strftime("%Y-%m-%d %H:%M:%S"),
                    duration,
                    vendor,
                    workers,
                    manager,
                    issue,
                ),
            )
            conn.commit()
            conn.close()
            st.success("등록 완료")

elif tab == "2. 설치 공정 관리":
    

    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM INSP", conn)
    conn.close()

    if not df.empty:
        col_search1, col_search2 = st.columns([1, 3])
        with col_search1:
            search_col = st.selectbox("검색 항목", ["전체"] + list(df.columns))
        with col_search2:
            search_term = st.text_input("검색어").upper()

        if search_term:
            if search_col == "전체":
                mask = df.astype(str).apply(
                    lambda x: x.str.contains(search_term, case=False).any(),
                    axis=1,
                )
                df = df[mask]
            else:
                df = df[
                    df[search_col]
                    .astype(str)
                    .str.contains(search_term, case=False)
                ]

        col_btn1, col_btn2, _ = st.columns([1, 1, 8])
        with col_btn1:
            select_all = st.checkbox("전체 선택")

        if "select_all_state" not in st.session_state:
            st.session_state.select_all_state = False

        if select_all != st.session_state.select_all_state:
            st.session_state.select_all_state = select_all
            df["선택"] = select_all
        else:
            df["선택"] = select_all

        df = df[
            [
                "선택",
                "id",
                "lot_no",
                "ship_no",
                "dwg_no",
                "unit_no",
                "weight",
                "receipt_date",
                "status",
                "start_time",
                "end_time",
                "duration",
                "vendor",
                "workers",
                "manager",
                "issue",
            ]
        ]

        unit_options = [
            "UNIT-A",
            "UNIT-B",
            "UNIT-C",
            "UNIT-D",
            "UNIT-E",
            "UNIT-F",
            "UNIT-G",
            "UNIT-H",
            "UNIT-I",
            "UNIT-J",
        ]
        status_options = ["설치 중", "보류", "파손", "완료", "출고"]
        vendor_options = ["AA", "BB", "CC"]

        edited_df = st.data_editor(
            df,
            column_config={
                "선택": st.column_config.CheckboxColumn(
                    "선택", default=False
                ),
                "id": st.column_config.NumberColumn("ID", disabled=True),
                "unit_no": st.column_config.SelectboxColumn(
                    "unit no", options=unit_options
                ),
                "status": st.column_config.SelectboxColumn(
                    "설치 진행 상황", options=status_options
                ),
                "vendor": st.column_config.SelectboxColumn(
                    "설치 업체", options=vendor_options
                ),
                "issue": st.column_config.TextColumn(
                    "이슈", width="medium"
                ),
            },
            disabled=["id", "lot_no", "duration"],
            hide_index=True,
            use_container_width=True,
        )

        col_act1, col_act2, _ = st.columns([1, 1, 8])

        with col_act1:
            if st.button("수정 저장"):
                conn = sqlite3.connect(DB_PATH)
                c = conn.cursor()
                for idx, row in edited_df.iterrows():
                    ship_no = str(row["ship_no"]).upper()
                    dwg_no = str(row["dwg_no"]).upper()
                    manager = str(row["manager"]).upper()
                    lot_no = f"{ship_no}-INST-{row['unit_no']}"

                    try:
                        s_dt = datetime.strptime(
                            str(row["start_time"]), "%Y-%m-%d %H:%M:%S"
                        )
                        e_dt = datetime.strptime(
                            str(row["end_time"]), "%Y-%m-%d %H:%M:%S"
                        )
                        duration = round(
                            (e_dt - s_dt).total_seconds() / 3600, 2
                        )
                    except Exception:
                        duration = row["duration"]

                    c.execute(
                        """
                        UPDATE INSP SET 
                            lot_no=?, ship_no=?, dwg_no=?, unit_no=?, weight=?, 
                            receipt_date=?, status=?, start_time=?, end_time=?, 
                            duration=?, vendor=?, workers=?, manager=?, issue=?
                        WHERE id=?
                    """,
                        (
                            lot_no,
                            ship_no,
                            dwg_no,
                            row["unit_no"],
                            row["weight"],
                            row["receipt_date"],
                            row["status"],
                            row["start_time"],
                            row["end_time"],
                            duration,
                            row["vendor"],
                            row["workers"],
                            manager,
                            row["issue"],
                            row["id"],
                        ),
                    )
                conn.commit()
                conn.close()
                st.success("수정 완료")
                st.rerun()

        with col_act2:
            if st.button("선택 삭제"):
                selected_ids = edited_df[edited_df["선택"] == True]["id"].tolist()
                if selected_ids:
                    conn = sqlite3.connect(DB_PATH)
                    c = conn.cursor()
                    c.executemany(
                        "DELETE FROM INSP WHERE id=?",
                        [(i,) for i in selected_ids],
                    )
                    conn.commit()
                    conn.close()
                    st.success("삭제 완료")
                    st.rerun()
                else:
                    st.warning("삭제할 항목을 선택하세요.")
    else:
        st.info("데이터가 없습니다.")