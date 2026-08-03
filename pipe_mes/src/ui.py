import pandas as pd # type: ignore
import streamlit as st

from src.db import DB_PATH, database_exists

# page_confit를 제목 함수로 수정
def setup_page(title: str):
    st.set_page_config(page_title=f"{title}")
# page_title을 개량한 커스텀 함수
def page_title(title: str, description: str, tables: str):
    st.title(title)
    st.info(
        f"""
        PWPMS: {description}

        DB테이블: {tables}

        """
    )
# DB 파일 연결 함수
def show_database_status():
    if database_exists():
        st.success(f"데이터베이스 연결 대상: {DB_PATH}")
    else:
        st.error(f"데이터베이스 파일을 찾을 수 없습니다: {DB_PATH}")

# Data base 빈 데이터 확인
def show_dataframe(df: pd.DataFrame, empty_message: str = "조건에 해당하는 데이터가 없습니다."):
    if df.empty:
        st.warning(empty_message)
    else:
        st.dataframe(df, use_container_width=True)

def metric_row(values: list[tuple[str, object]]):
    columns = st.columns(len(values))
    for column, (label, value) in zip(columns, values):
        column.metric(label, value)

def row_to_dict(row):
    if row is None:
        return {}
    return {key: row[key] for key in row.keys()}