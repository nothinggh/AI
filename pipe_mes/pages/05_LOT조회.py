import sqlite3
from pathlib import Path

import pandas as pd # type: ignore
import streamlit as st


BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "sql" / "pipe_mes.db"


def database_exists() -> bool:
    return DB_PATH.exists()


def get_connection() -> sqlite3.Connection:
    if not database_exists():
        raise FileNotFoundError(f"SQLite database file was not found: {DB_PATH}")
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def fetch_dataframe(sql: str, params: tuple = ()) -> pd.DataFrame:
    with get_connection() as connection:
        return pd.read_sql_query(sql, connection, params=params)


@st.cache_data(show_spinner=False)
def load_joined_data(direction: str, db_mtime: float) -> pd.DataFrame:
    if direction == "forward":
        query = """
            SELECT
                m.lot_no AS mfp_lot_no,
                m.dwg_no AS mfp_dwg_no,
                m.receipt_date AS mfp_receipt_date,
                m.issue_desc AS mfp_issue_desc,
                i.unit_no AS insp_unit_no,
                i.status AS insp_status,
                i.vendor AS insp_vendor,
                y.block_no AS ydp_block_no,
                y.area AS ydp_area,
                y.progress AS ydp_progress
            FROM MFP AS m
            LEFT JOIN INSP AS i
                ON m.dwg_no = i.dwg_no
            LEFT JOIN YDP AS y
                ON i.ship_no = y.ship_no
               AND i.unit_no = y.unit_no
        """
    else:
        query = """
            SELECT
                y.lot_no AS ydp_lot_no,
                y.block_no AS ydp_block_no,
                y.area AS ydp_area,
                y.progress AS ydp_progress,
                y.issue AS ydp_issue,
                i.unit_no AS insp_unit_no,
                i.status AS insp_status,
                i.vendor AS insp_vendor,
                m.dwg_no AS mfp_dwg_no,
                m.receipt_date AS mfp_receipt_date
            FROM YDP AS y
            LEFT JOIN INSP AS i
                ON y.ship_no = i.ship_no
               AND y.unit_no = i.unit_no
            LEFT JOIN MFP AS m
                ON i.dwg_no = m.dwg_no
        """
    return fetch_dataframe(query)


def filter_data(data: pd.DataFrame, keyword: str, search_column: str = "\uc804\uccb4") -> pd.DataFrame:
    keyword = keyword.strip()
    if not keyword:
        return data

    searchable_data = data if search_column == "\uc804\uccb4" else data[[search_column]]
    matches = searchable_data.fillna("").astype(str).apply(
        lambda column: column.str.contains(keyword, case=False, regex=False)
    )
    return data.loc[matches.any(axis=1)]


def render_tab(direction: str) -> None:
    try:
        data = load_joined_data(direction, DB_PATH.stat().st_mtime)
    except (FileNotFoundError, sqlite3.Error, pd.errors.DatabaseError) as error:
        st.error(str(error))
        return

    option_column, keyword_column = st.columns([1, 3])
    with option_column:
        search_column = st.selectbox(
            "\uac80\uc0c9 \ud56d\ubaa9",
            ["\uc804\uccb4", *data.columns.tolist()],
            key=f"option_{direction}",
        )
    with keyword_column:
        keyword = st.text_input(
            "\uac80\uc0c9\uc5b4 \uc785\ub825",
            placeholder="LOT, DWG, UNIT, STATUS, VENDOR, BLOCK, AREA, PROGRESS \uac80\uc0c9",
            key=f"keyword_{direction}",
        )

    filtered_data = filter_data(data, keyword, search_column)
    total_column, result_column = st.columns(2)
    total_column.metric("\uc804\uccb4 \ud589\uc218", f"{len(data):,}\uac74")
    result_column.metric("\uac80\uc0c9\ub41c \ud589\uc218", f"{len(filtered_data):,}\uac74")
    st.dataframe(filtered_data, use_container_width=True, hide_index=True)


st.set_page_config(page_title="PIPE MES \ud1b5\ud569 \uc870\ud68c", layout="wide")
st.title("🔍 LOT \ud1b5\ud569 \uc870\ud68c")
# st.caption(f"DB \uacbd\ub85c: {DB_PATH}")
# st.caption("JOIN: MFP.dwg_no = INSP.dwg_no, INSP.ship_no + unit_no = YDP.ship_no + unit_no")

forward_tab, reverse_tab = st.tabs([
    "\uc815\ubc29\ud5a5 (제작 \u2192 설치 \u2192 YARD)",
    "\uc5ed\ubc29\ud5a5 (YARD \u2192 설치 \u2192 제작)",
])

with forward_tab:
    render_tab("forward")

with reverse_tab:
    render_tab("reverse")