import sqlite3
from pathlib import Path

import pandas as pd # type: ignore
import streamlit as st


BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "sql" / "pipe_mes.db"
ALLOWED_TABLES = ("bom", "mfp", "insp", "ydp")


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


def fetch_one(sql: str, params: tuple = ()) -> sqlite3.Row | None:
    with get_connection() as connection:
        return connection.execute(sql, params).fetchone()


def fetch_all(sql: str, params: tuple = ()) -> list[sqlite3.Row]:
    with get_connection() as connection:
        return connection.execute(sql, params).fetchall()


@st.cache_data(show_spinner=False)
def get_available_tables(db_mtime: float) -> list[str]:
    query = "SELECT name FROM sqlite_master WHERE type = 'table'"
    names = {row["name"].lower() for row in fetch_all(query)}
    return [name for name in ALLOWED_TABLES if name in names]


@st.cache_data(show_spinner=False)
def load_table(table_name: str, db_mtime: float) -> pd.DataFrame:
    if table_name not in ALLOWED_TABLES:
        raise ValueError("Unsupported table name")
    return fetch_dataframe(f'SELECT * FROM "{table_name}"')


@st.cache_data(show_spinner=False)
def get_total_rows(table_names: tuple[str, ...], db_mtime: float) -> int:
    total = 0
    for table_name in table_names:
        if table_name not in ALLOWED_TABLES:
            continue
        row = fetch_one(f'SELECT COUNT(*) AS row_count FROM "{table_name}"')
        total += row["row_count"]
    return total


def search_all_tables(table_names: list[str], keyword: str, db_mtime: float) -> pd.DataFrame:
    results: list[pd.DataFrame] = []
    for table_name in table_names:
        result = filter_data(load_table(table_name, db_mtime), keyword)
        if not result.empty:
            result = result.copy()
            result.insert(0, "table_name", table_name.upper())
            results.append(result)
    return pd.concat(results, ignore_index=True, sort=False) if results else pd.DataFrame()


def filter_data(data: pd.DataFrame, keyword: str) -> pd.DataFrame:
    keyword = keyword.strip()
    if not keyword:
        return data

    matches = data.fillna("").astype(str).apply(
        lambda column: column.str.contains(keyword, case=False, regex=False)
    )
    return data.loc[matches.any(axis=1)]


st.set_page_config(page_title="PIPE MES \ud14c\uc774\ube14 \uc870\ud68c", layout="wide")
st.title("🔍 전체 \ud14c\uc774\ube14 \uc870\ud68c")
# st.caption(f"DB \uacbd\ub85c: {DB_PATH}")

try:
    db_mtime = DB_PATH.stat().st_mtime
    tables = get_available_tables(db_mtime)
    if not tables:
        st.warning("DB\uc5d0 BOM, MFP, INSP, YDP \ud14c\uc774\ube14\uc774 \uc5c6\uc2b5\ub2c8\ub2e4.")
        st.stop()

    left, right = st.columns([1, 3])
    with left:
        selected_table = st.selectbox(
            "\ud14c\uc774\ube14 \uc120\ud0dd",
            ["\uc804\uccb4", *tables],
            index=0,
            format_func=lambda value: value if value == "\uc804\uccb4" else value.upper(),
        )
    with right:
        keyword = st.text_input(
            "\uac80\uc0c9\uc5b4 \uc785\ub825",
            placeholder="\uc120\ud0dd\ud55c \ud14c\uc774\ube14\uc758 \ubaa8\ub4e0 \uceec\ub7fc\uc5d0\uc11c \uac80\uc0c9",
        )

    if selected_table == "\uc804\uccb4":
        total_rows = get_total_rows(tuple(tables), db_mtime)
        filtered_data = search_all_tables(tables, keyword, db_mtime) if keyword.strip() else pd.DataFrame()
    else:
        data = load_table(selected_table, db_mtime)
        total_rows = len(data)
        filtered_data = filter_data(data, keyword)

    total_column, result_column = st.columns(2)
    total_column.metric("\uc804\uccb4 \ud589\uc218", f"{total_rows:,}\uac74")
    result_column.metric("\uac80\uc0c9\ub41c \ud589\uc218", f"{len(filtered_data):,}\uac74")

    if selected_table == "\uc804\uccb4" and not keyword.strip():
        st.info("\uc804\uccb4 \uac80\uc0c9\uc744 \uc704\ud55c \uac80\uc0c9\uc5b4\ub97c \uc785\ub825\ud574 \uc8fc\uc138\uc694.")
    else:
        st.dataframe(filtered_data, use_container_width=True, hide_index=True)
except (FileNotFoundError, sqlite3.Error, pd.errors.DatabaseError, ValueError) as error:
    st.error(str(error))