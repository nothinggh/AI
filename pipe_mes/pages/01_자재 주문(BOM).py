import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

st.set_page_config(layout="wide")

DB_PATH = "/home/gram/work/pipe_mes/sql/pipe_mes.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS BOM (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id TEXT,
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
    ''')
    conn.commit()
    conn.close()

init_db()

WEIGHT_DATA = {
    "PIPE(6M)": {"8A": 3.8, "10A": 5.1, "15A": 7.9, "20A": 10.1, "25A": 16.0, "32A": 20.3, "40A": 23.3, "50A": 31.9, "65A": 44.2, "80A": 51.5, "100A": 72.5},
    "FLANGE": {"8A": 0.4, "10A": 0.5, "15A": 0.7, "20A": 0.9, "25A": 1.2, "32A": 1.6, "40A": 1.9, "50A": 2.5, "65A": 3.4, "80A": 4.1, "100A": 5.6},
    "COUPLING": {"8A": 0.1, "10A": 0.12, "15A": 0.2, "20A": 0.3, "25A": 0.45, "32A": 0.6, "40A": 0.8, "50A": 1.2, "65A": 1.8, "80A": 2.3, "100A": 3.5},
    "BOLT": {"8A": 0.05, "10A": 0.05, "15A": 0.08, "20A": 0.08, "25A": 0.1, "32A": 0.12, "40A": 0.15, "50A": 0.2, "65A": 0.25, "80A": 0.3, "100A": 0.4},
    "NUT": {"8A": 0.02, "10A": 0.02, "15A": 0.03, "20A": 0.03, "25A": 0.04, "32A": 0.05, "40A": 0.06, "50A": 0.08, "65A": 0.1, "80A": 0.12, "100A": 0.15},
    "GASKET": {"8A": 0.01, "10A": 0.01, "15A": 0.02, "20A": 0.02, "25A": 0.03, "32A": 0.04, "40A": 0.05, "50A": 0.07, "65A": 0.09, "80A": 0.11, "100A": 0.15},
    "ELBOW": {"8A": 0.1, "10A": 0.15, "15A": 0.25, "20A": 0.35, "25A": 0.55, "32A": 0.85, "40A": 1.1, "50A": 1.8, "65A": 2.9, "80A": 4.0, "100A": 6.8},
    "TEE": {"8A": 0.15, "10A": 0.2, "15A": 0.35, "20A": 0.5, "25A": 0.8, "32A": 1.2, "40A": 1.5, "50A": 2.4, "65A": 3.8, "80A": 5.2, "100A": 8.5}
}

PRICE_DATA = {
    "PIPE(6M)": {"8A": 12000, "10A": 15000, "15A": 22000, "20A": 28000, "25A": 38000, "32A": 49000, "40A": 55000, "50A": 73000, "65A": 98000, "80A": 115000, "100A": 158000},
    "FLANGE": {"8A": 3500, "10A": 4000, "15A": 5500, "20A": 7000, "25A": 9500, "32A": 12000, "40A": 14500, "50A": 18500, "65A": 24000, "80A": 29000, "100A": 39000},
    "COUPLING": {"8A": 1200, "10A": 1500, "15A": 2000, "20A": 2600, "25A": 3500, "32A": 4800, "40A": 5800, "50A": 8200, "65A": 12000, "80A": 15000, "100A": 22000},
    "BOLT": {"8A": 300, "10A": 350, "15A": 500, "20A": 600, "25A": 800, "32A": 1000, "40A": 1200, "50A": 1500, "65A": 2000, "80A": 2500, "100A": 3200},
    "NUT": {"8A": 150, "10A": 180, "15A": 250, "20A": 300, "25A": 400, "32A": 500, "40A": 600, "50A": 800, "65A": 1000, "80A": 1200, "100A": 1600},
    "GASKET": {"8A": 500, "10A": 600, "15A": 800, "20A": 1000, "25A": 1300, "32A": 1700, "40A": 2000, "50A": 2700, "65A": 3500, "80A": 4200, "100A": 5800},
    "ELBOW": {"8A": 1500, "10A": 1800, "15A": 2500, "20A": 3300, "25A": 4500, "32A": 6200, "40A": 7500, "50A": 10500, "65A": 15000, "80A": 19000, "100A": 28000},
    "TEE": {"8A": 2000, "10A": 2400, "15A": 3300, "20A": 4500, "25A": 6000, "32A": 8200, "40A": 10000, "50A": 14000, "65A": 20000, "80A": 25000, "100A": 37000}
}

ALL_SIZES = ["8A", "10A", "15A", "20A", "25A", "32A", "40A", "50A", "65A", "80A", "100A"]
ALL_MATERIALS = ["STEEL", "SUS", "COPPER", "ASBESTOS", "RUBBER"]
ALL_ITEMS = ["PIPE(6M)", "FLANGE", "COUPLING", "BOLT", "NUT", "GASKET", "ELBOW", "TEE"]

st.markdown("---")
st.title("자재 주문(BOM)")
st.markdown("##### (Bill Of Materials)")
st.markdown("---")

tab_choice = st.radio("", ["1. 자재 주문 등록", "2. 전체 주문 관리"], horizontal=True)

if tab_choice == "1. 자재 주문 등록":
    col1, col2 = st.columns(2)
    with col1:
        order_id = st.text_input("주문자 ID").strip().upper()
        ship_no = st.text_input("호선 번호").strip().upper()
        item_type = st.selectbox("자재 종류", ALL_ITEMS)
        material = st.selectbox("재질", ALL_MATERIALS)

    if material in ["STEEL", "SUS"]:
        available_sizes = [s for s in ALL_SIZES if s not in ["8A", "10A"]]
    elif material == "COPPER":
        available_sizes = ["8A", "10A"]
    else:
        available_sizes = ALL_SIZES

    with col2:
        size = st.selectbox("SIZE", available_sizes)
        quantity = st.number_input("수량", min_value=1, value=1, step=1)

        unit_weight = WEIGHT_DATA.get(item_type, {}).get(size, 0.0)
        unit_price = PRICE_DATA.get(item_type, {}).get(size, 0.0)

        weight = st.number_input("중량 (개당/단위 kg)", value=float(unit_weight), disabled=True)
        price = st.number_input("가격 (개당/단위 원)", value=float(unit_price), disabled=True)

    order_date = st.date_input("주문 날짜", datetime.now()).strftime("%Y-%m-%d")
    request_note = st.text_area("요청 사항").strip().upper()

    if st.button("주문 등록"):
        if not order_id or not ship_no:
            st.warning("주문자 ID와 호선 번호를 입력하세요.")
        else:
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            c.execute('''
                INSERT INTO BOM (order_id, ship_no, item_type, material, size, quantity, weight, price, order_date, request_note)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (order_id, ship_no, item_type, material, size, quantity, weight, price, order_date, request_note))
            conn.commit()
            conn.close()
            st.success("등록되었습니다.")

elif tab_choice == "2. 전체 주문 관리":
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM BOM", conn)
    conn.close()

    search_col = st.selectbox("검색 항목", ["전체"] + list(df.columns) if not df.empty else ["전체"])
    search_keyword = st.text_input("검색어").strip().upper()

    if not df.empty and search_keyword:
        if search_col == "전체":
            mask = df.astype(str).apply(lambda row: row.str.contains(search_keyword, case=False).any(), axis=1)
            df = df[mask]
        else:
            df = df[df[search_col].astype(str).str.contains(search_keyword, case=False)]

    col_btn1, col_btn2, _ = st.columns([1, 1, 8])
    with col_btn1:
        select_all = st.checkbox("전체 선택")

    if 'select_state' not in st.session_state:
        st.session_state.select_state = {}

    if select_all:
        for row_id in df['id']:
            st.session_state.select_state[row_id] = True

    df.insert(0, "선택", df['id'].map(lambda x: st.session_state.select_state.get(x, False if not select_all else True)))

    edited_df = st.data_editor(
        df,
        column_config={
            "선택": st.column_config.CheckboxColumn("선택", default=False),
            "id": st.column_config.NumberColumn("ID", disabled=True),
            "order_id": st.column_config.TextColumn("주문자 ID"),
            "ship_no": st.column_config.TextColumn("호선 번호"),
            "item_type": st.column_config.SelectboxColumn("자재 종류", options=ALL_ITEMS),
            "material": st.column_config.SelectboxColumn("재질", options=ALL_MATERIALS),
            "size": st.column_config.SelectboxColumn("SIZE", options=ALL_SIZES),
            "quantity": st.column_config.NumberColumn("수량", min_value=1, step=1),
            "weight": st.column_config.NumberColumn("중량"),
            "price": st.column_config.NumberColumn("가격"),
            "order_date": st.column_config.TextColumn("주문 날짜"),
            "request_note": st.column_config.TextColumn("요청 사항")
        },
        disabled=["id"],
        use_container_width=True,
        hide_index=True
    )

    c1, c2 = st.columns([1, 1])
    with c1:
        if st.button("수정 사항 저장"):
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            for _, row in edited_df.iterrows():
                mat = str(row['material']).upper()
                sz = str(row['size']).upper()
                
                if mat in ["STEEL", "SUS"] and sz in ["8A", "10A"]:
                    st.error(f"ID {row['id']}: STEEL, SUS 재질은 8A, 10A 규격을 사용할 수 없습니다.")
                    conn.close()
                    st.stop()
                if mat == "COPPER" and sz not in ["8A", "10A"]:
                    st.error(f"ID {row['id']}: COPPER 재질은 8A, 10A 규격만 사용 가능합니다.")
                    conn.close()
                    st.stop()

                c.execute('''
                    UPDATE BOM SET
                        order_id = ?,
                        ship_no = ?,
                        item_type = ?,
                        material = ?,
                        size = ?,
                        quantity = ?,
                        weight = ?,
                        price = ?,
                        order_date = ?,
                        request_note = ?
                    WHERE id = ?
                ''', (
                    str(row['order_id']).upper(),
                    str(row['ship_no']).upper(),
                    str(row['item_type']).upper(),
                    mat,
                    sz,
                    int(row['quantity']),
                    float(row['weight']),
                    float(row['price']),
                    str(row['order_date']),
                    str(row['request_note']).upper(),
                    int(row['id'])
                ))
            conn.commit()
            conn.close()
            st.success("수정 사항이 저장되었습니다.")
            st.rerun()

    with c2:
        if st.button("선택 항목 삭제"):
            selected_ids = edited_df[edited_df["선택"] == True]["id"].tolist()
            if selected_ids:
                conn = sqlite3.connect(DB_PATH)
                c = conn.cursor()
                c.executemany("DELETE FROM BOM WHERE id = ?", [(x,) for x in selected_ids])
                conn.commit()
                conn.close()
                st.success("선택한 항목이 삭제되었습니다.")
                st.rerun()
            else:
                st.warning("삭제할 항목을 선택하세요.")