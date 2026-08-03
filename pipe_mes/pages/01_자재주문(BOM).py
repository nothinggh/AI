import sqlite3
import pandas as pd # type: ignore
import streamlit as st
from datetime import datetime

st.set_page_config(layout="wide")


DB_PATH = "/home/gram/work/pipe_mes/sql/pipe_mes.db"


def init_db():

    conn = sqlite3.connect(DB_PATH)

    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS BOM (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            ship_no TEXT,
            item_type TEXT,
            material TEXT,
            size TEXT,
            quantity INTEGER,
            weight REAL,
            price REAL,
            order_date TEXT,
            request_note TEXT
        )
    """)

    conn.commit()
    conn.close()


init_db()


WEIGHT_DATA = {
    "PIPE(6M)": {
        "8A": 3.0,
        "10A": 4.0,
        "15A": 5.1,
        "20A": 6.8,
        "25A": 10.1,
        "32A": 13.7,
        "40A": 16.0,
        "50A": 21.5,
        "65A": 30.5,
        "80A": 36.2,
        "100A": 51.0,
    },
    "FLANGE": {
        "15A": 0.8,
        "20A": 1.0,
        "25A": 1.4,
        "32A": 2.0,
        "40A": 2.2,
        "50A": 2.8,
        "65A": 3.8,
        "80A": 4.5,
        "100A": 5.6,
    },
    "COUPLING": {
        "15A": 0.15,
        "20A": 0.2,
        "25A": 0.3,
        "32A": 0.45,
        "40A": 0.55,
        "50A": 0.8,
        "65A": 1.2,
        "80A": 1.6,
        "100A": 2.3,
    },
    "BOLT": {
        "15A": 0.1,
        "20A": 0.1,
        "25A": 0.12,
        "32A": 0.15,
        "40A": 0.15,
        "50A": 0.2,
        "65A": 0.2,
        "80A": 0.25,
        "100A": 0.3,
    },
    "NUT": {
        "15A": 0.05,
        "20A": 0.05,
        "25A": 0.06,
        "32A": 0.08,
        "40A": 0.08,
        "50A": 0.1,
        "65A": 0.1,
        "80A": 0.12,
        "100A": 0.15,
    },
    "GASKET": {
        "15A": 0.03,
        "20A": 0.04,
        "25A": 0.05,
        "32A": 0.06,
        "40A": 0.07,
        "50A": 0.09,
        "65A": 0.12,
        "80A": 0.15,
        "100A": 0.2,
    },
    "ELBOW": {
        "15A": 0.2,
        "20A": 0.3,
        "25A": 0.5,
        "32A": 0.8,
        "40A": 1.0,
        "50A": 1.6,
        "65A": 2.6,
        "80A": 3.7,
        "100A": 6.5,
    },
    "TEE": {
        "15A": 0.3,
        "20A": 0.4,
        "25A": 0.7,
        "32A": 1.1,
        "40A": 1.4,
        "50A": 2.1,
        "65A": 3.5,
        "80A": 4.8,
        "100A": 8.2,
    },
}
PRICE_DATA = {
    "PIPE(6M)": {
        "8A": 12000,
        "10A": 15000,
        "15A": 18000,
        "20A": 23000,
        "25A": 31000,
        "32A": 42000,
        "40A": 48000,
        "50A": 63000,
        "65A": 88000,
        "80A": 105000,
        "100A": 145000,
    },
    "FLANGE": {
        "15A": 4500,
        "20A": 5500,
        "25A": 7000,
        "32A": 9000,
        "40A": 11000,
        "50A": 14000,
        "65A": 19000,
        "80A": 23000,
        "100A": 31000,
    },
    "COUPLING": {
        "15A": 1200,
        "20A": 1500,
        "25A": 2000,
        "32A": 2800,
        "40A": 3500,
        "50A": 4800,
        "65A": 7000,
        "80A": 9500,
        "100A": 13000,
    },
    "BOLT": {
        "15A": 500,
        "20A": 500,
        "25A": 600,
        "32A": 700,
        "40A": 700,
        "50A": 900,
        "65A": 900,
        "80A": 1200,
        "100A": 1500,
    },
    "NUT": {
        "15A": 300,
        "20A": 300,
        "25A": 350,
        "32A": 400,
        "40A": 400,
        "50A": 500,
        "65A": 500,
        "80A": 700,
        "100A": 900,
    },
    "GASKET": {
        "15A": 800,
        "20A": 1000,
        "25A": 1200,
        "32A": 1500,
        "40A": 1800,
        "50A": 2300,
        "65A": 3000,
        "80A": 3800,
        "100A": 5000,
    },
    "ELBOW": {
        "15A": 1500,
        "20A": 2000,
        "25A": 2800,
        "32A": 4000,
        "40A": 5200,
        "50A": 7500,
        "65A": 12000,
        "80A": 16000,
        "100A": 25000,
    },
    "TEE": {
        "15A": 2200,
        "20A": 2900,
        "25A": 4000,
        "32A": 5800,
        "40A": 7500,
        "50A": 10500,
        "65A": 17000,
        "80A": 23000,
        "100A": 36000,
    },
}


MATERIALS = ["STEEL", "SUS", "COPPER", "ASBESTOS", "RUBBER"]


SIZES = ["8A", "10A", "15A", "20A", "25A", "32A", "40A", "50A", "65A", "80A", "100A"]


ITEMS = ["PIPE(6M)", "FLANGE", "COUPLING", "BOLT", "NUT", "GASKET", "ELBOW", "TEE"]



st.title("📦 자재 주문(BOM)")

st.markdown("##### (Bill Of Materials)")

st.markdown("---")


tab_choice = st.radio("", ["1. 자재 주문 등록", "2. 전체 주문 관리"], horizontal=True)


if tab_choice == "1. 자재 주문 등록":

    col1, col2 = st.columns(2)

    with col1:

        user_id = st.text_input("주문자 ID").upper()

        ship_no = st.text_input("호선 번호").upper()

        item_type = st.selectbox("자재 종류", ITEMS)

        material = st.selectbox("재질", MATERIALS)

    with col2:

        size = st.selectbox("SIZE", SIZES)

        quantity = st.number_input("수량", min_value=1, value=1)

        order_date = st.date_input("주문 날짜", datetime.now()).strftime("%Y-%m-%d")

        request_note = st.text_area("요청 사항").upper()

    unit_weight = WEIGHT_DATA.get(item_type, {}).get(size, 0.0)

    unit_price = PRICE_DATA.get(item_type, {}).get(size, 0)

    total_weight = round(unit_weight * quantity, 2)

    total_price = round(unit_price * quantity, 0)

    st.write(f"개당 중량 : {unit_weight} kg / 총 중량 : {total_weight} kg")

    st.write(f"개당 가격 : {unit_price:,} 원 / 총 가격 : {total_price:,} 원")

    if st.button("등록"):

        if user_id == "":

            st.error("주문자 ID를 입력하세요.")

        elif ship_no == "":

            st.error("호선 번호를 입력하세요.")

        elif material in ["STEEL", "SUS"] and size in ["8A", "10A"]:

            st.error("STEEL 및 SUS 재질은 8A,10A 주문 불가")

        elif material == "COPPER" and size not in ["8A", "10A"]:

            st.error("COPPER는 8A,10A만 주문 가능")

        else:

            conn = sqlite3.connect(DB_PATH)

            cursor = conn.cursor()

            cursor.execute(
                """
                INSERT INTO BOM
                (
                    user_id,
                    ship_no,
                    item_type,
                    material,
                    size,
                    quantity,
                    weight,
                    price,
                    order_date,
                    request_note
                )
                VALUES
                (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    user_id,
                    ship_no,
                    item_type,
                    material,
                    size,
                    quantity,
                    total_weight,
                    total_price,
                    order_date,
                    request_note,
                ),
            )

            conn.commit()

            conn.close()

            st.success("자재 주문 등록 완료")
elif tab_choice == "2. 전체 주문 관리":

    conn = sqlite3.connect(DB_PATH)

    df = pd.read_sql_query("SELECT * FROM BOM", conn)

    conn.close()

    col_search1, col_search2 = st.columns(2)

    with col_search1:

        search_col = st.selectbox("검색 컬럼 선택", ["전체"] + list(df.columns))

    with col_search2:

        search_kw = st.text_input("검색어 입력").upper()

    if search_kw:

        if search_col == "전체":

            mask = (
                df.astype(str)
                .apply(lambda x: x.str.contains(search_kw, case=False))
                .any(axis=1)
            )

            df = df[mask]

        else:

            df = df[df[search_col].astype(str).str.contains(search_kw, case=False)]

    if "select_all" not in st.session_state:

        st.session_state.select_all = False

    def toggle_all():

        st.session_state.select_all = st.session_state.chk_all

    st.checkbox("전체 선택", key="chk_all", on_change=toggle_all)

    if not df.empty:

        df.insert(0, "선택", st.session_state.select_all)

        edited_df = st.data_editor(
            df,
            column_config={
                "id": st.column_config.Column("ID", disabled=True),
                "user_id": st.column_config.TextColumn("주문자 ID"),
                "ship_no": st.column_config.TextColumn("호선 번호"),
                "item_type": st.column_config.SelectboxColumn(
                    "자재 종류", options=ITEMS
                ),
                "material": st.column_config.SelectboxColumn("재질", options=MATERIALS),
                "size": st.column_config.SelectboxColumn("SIZE", options=SIZES),
                "quantity": st.column_config.NumberColumn("수량"),
                "weight": st.column_config.NumberColumn("중량"),
                "price": st.column_config.NumberColumn("가격"),
                "order_date": st.column_config.TextColumn("주문 날짜"),
                "request_note": st.column_config.TextColumn("요청 사항"),
            },
            hide_index=True,
            use_container_width=True,
        )

        col1, col2 = st.columns(2)

        with col1:

            if st.button("선택 항목 수정 저장"):

                conn = sqlite3.connect(DB_PATH)

                cursor = conn.cursor()

                for _, row in edited_df.iterrows():

                    item_type = str(row["item_type"]).upper()

                    material = str(row["material"]).upper()

                    size = str(row["size"]).upper()

                    quantity = int(row["quantity"])

                    unit_weight = WEIGHT_DATA.get(item_type, {}).get(size, 0.0)

                    unit_price = PRICE_DATA.get(item_type, {}).get(size, 0)

                    total_weight = round(unit_weight * quantity, 2)

                    total_price = round(unit_price * quantity, 0)

                    if material in ["STEEL", "SUS"] and size in ["8A", "10A"]:

                        st.error(f"ID {row['id']} : STEEL/SUS 8A,10A 불가")

                        continue

                    if material == "COPPER" and size not in ["8A", "10A"]:

                        st.error(f"ID {row['id']} : COPPER SIZE 오류")

                        continue

                    cursor.execute(
                        """
                        UPDATE BOM SET

                        user_id=?,
                        ship_no=?,
                        item_type=?,
                        material=?,
                        size=?,
                        quantity=?,
                        weight=?,
                        price=?,
                        order_date=?,
                        request_note=?

                        WHERE id=?

                        """,
                        (
                            str(row["user_id"]).upper(),
                            str(row["ship_no"]).upper(),
                            item_type,
                            material,
                            size,
                            quantity,
                            total_weight,
                            total_price,
                            str(row["order_date"]),
                            str(row["request_note"]).upper(),
                            int(row["id"]),
                        ),
                    )

                conn.commit()

                conn.close()

                st.success("수정 사항 저장 완료")

                st.rerun()

        with col2:

            if st.button("선택 항목 삭제"):

                selected_ids = edited_df[edited_df["선택"] == True]["id"].tolist()

                if selected_ids:

                    conn = sqlite3.connect(DB_PATH)

                    cursor = conn.cursor()

                    cursor.executemany(
                        """
                        DELETE FROM BOM
                        WHERE id=?
                        """,
                        [(i,) for i in selected_ids],
                    )

                    conn.commit()

                    conn.close()

                    st.success("삭제 완료")

                    st.rerun()

                else:

                    st.warning("삭제할 항목을 선택해주세요.")