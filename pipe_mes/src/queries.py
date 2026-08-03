import streamlit as st
import pandas as pd  # type: ignore

from src.db import fetch_dataframe, fetch_all, fetch_one


def table_counts():
    return fetch_dataframe("""
        SELECT 'BOM' AS table_name, COUNT(*) AS row_count FROM BOM
        UNION ALL
        SELECT 'MFP' AS table_name, COUNT(*) AS row_count FROM MFP
        UNION ALL
        SELECT 'INSP' AS table_name, COUNT(*) AS row_count FROM INSP
        UNION ALL
        SELECT 'YDP' AS table_name, COUNT(*) AS row_count FROM YDP
        """)


##########################################################################


def table_list():
    return fetch_dataframe("""
        SELECT name AS table_name
        FROM sqlite_master
        WHERE type = 'table'
        ORDER BY name
        """)


##########################################################################


def bom_summary_by_ship(keyword: str = ""):
    """호선(ship_no)별 BOM 총수량, 총중량, 총금액을 집계합니다."""
    where = ["ship_no IS NOT NULL AND ship_no != ''"]
    params = []

    if keyword:
        where.append("ship_no LIKE ?")
        params.append(f"%{keyword}%")

    where_clause = " AND ".join(where)

    return fetch_dataframe(
        f"""
        SELECT
            ship_no,
            COALESCE(SUM(quantity), 0) AS total_quantity,
            ROUND(COALESCE(SUM(weight), 0), 2) AS total_weight,
            COALESCE(SUM(price * quantity), 0) AS total_price
        FROM BOM
        WHERE {where_clause}
        GROUP BY ship_no
        ORDER BY ship_no
        """,
        tuple(params),
    )


##########################################################################


def item_type_counts():
    """품목 타입(item_type)별 수량, 중량, 금액 집계"""
    return fetch_dataframe("""
        SELECT 
            item_type,
            COALESCE(SUM(quantity), 0) AS total_quantity,
            ROUND(COALESCE(SUM(weight), 0), 2) AS total_weight,
            COALESCE(SUM(price * quantity), 0) AS total_price
        FROM BOM
        GROUP BY item_type
        ORDER BY item_type
        """)


##########################################################################


def bom_by_ship_no(ship_no: str):
    return fetch_dataframe(
        """
        SELECT 
            id,
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
        FROM BOM
        WHERE ship_no = ?
        ORDER BY id
        """,
        (ship_no,),
    )


##########################################################################


def get_ship_summary_df():
    query = """
    SELECT 
        ship_no AS ship_no,
        manager AS manufacturer,
        COUNT(DISTINCT unit_no) AS drawing_count,
        COUNT(CASE WHEN issue IS NOT NULL AND TRIM(issue) <> '' THEN 1 END) AS issue_count,
        SUM(actual_hours) AS total_hours,
        SUM(headcount) AS total_headcount,
        SUM(actual_hours * headcount) AS total_man_hours
    FROM YDP
    GROUP BY ship_no, manager;
    """
    df = fetch_dataframe(query)
    df.columns = [
        "호선 번호",
        "제작업체",
        "도면 갯수",
        "이슈 건수",
        "토탈 실투입 시간",
        "작업자 수",
        "총 공수(M/H)",
    ]
    return df


df_result = get_ship_summary_df()
print(df_result)

##########################################################################


def load_drawing_status(target_hulls: list[str] | None = None) -> pd.DataFrame:
    """DB(MFP 테이블)에서 데이터를 조회하여 호선별 집계 데이터를 생성합니다."""

    # 1. SQL 쿼리문 (dwg_type, vendor 제외)
    query = """
        SELECT 
            ship_no,
            status,
            issue_type,
            worker
        FROM MFP
    """
    df = fetch_dataframe(query)

    # DB가 완전히 비어있는 경우 빈 DataFrame 반환
    if df.empty:
        return pd.DataFrame()

    # target_hulls가 지정되지 않았으면 DB에 존재하는 모든 호선 대상
    if target_hulls is None:
        target_hulls = sorted(
            [s for s in df["ship_no"].dropna().unique() if str(s).strip()]
        )

    summary_list = []

    for hull in target_hulls:
        df_hull = df[df["ship_no"] == hull]

        # 도면 등록이 1건도 없는 호선 처리
        if df_hull.empty:
            summary_list.append(
                {
                    "ship_no": hull,
                    "도면건수": 0,
                    "진행상황": "작업 전",
                    "완료건수": 0,
                    "이슈건수": 0,
                    "작업자": "-",
                }
            )
        else:
            total_count = len(df_hull)

            # status가 '완료'인 항목 카운트 (공백 예외 처리)
            completed_count = (
                df_hull["status"].fillna("").astype(str).str.strip().eq("완료").sum()
            )

            # issue_type이 '없음', 공백, 'nan'이 아닌 항목 카운트
            issue_series = df_hull["issue_type"].fillna("").astype(str).str.strip()
            issue_count = (
                (issue_series != "없음")
                & (issue_series != "")
                & (issue_series.str.lower() != "nan")
            ).sum()

            # 진행상황 판정
            current_status = (
                "완료"
                if (total_count > 0 and completed_count == total_count)
                else "진행 중"
            )

            # 작업자 목록 (중복, NaN, 빈값 제거 후 연결)
            unique_workers = [
                w
                for w in df_hull["worker"].dropna().astype(str).str.strip().unique()
                if w and w.lower() != "nan"
            ]
            workers = ", ".join(unique_workers) if unique_workers else "-"

            summary_list.append(
                {
                    "ship_no": hull,
                    "도면건수": total_count,
                    "진행상황": current_status,
                    "완료건수": completed_count,
                    "이슈건수": issue_count,
                    "작업자": workers,
                }
            )

    return pd.DataFrame(summary_list)


##########################################################################

def load_insp_status():

    query = """
    SELECT
        ship_no,
        unit_no,
        COUNT(*) AS cnt,
        SUM(weight) AS weight_kg,
        SUM(CASE WHEN status='완료' THEN 1 ELSE 0 END) AS completed,
        SUM(
            CASE
                WHEN TRIM(COALESCE(issue,'')) NOT IN ('','없음')
                THEN 1
                ELSE 0
            END
        ) AS issues,
        SUM(duration) AS hours,
        SUM(workers) AS workers

    FROM INSP
    GROUP BY ship_no, unit_no
    ORDER BY ship_no, unit_no
    """

    return fetch_dataframe(query)


##########################################################################


def load_ydp_status():

    query = """
    SELECT
        ship_no,
        block_no,

        COUNT(*) AS total_cnt,

        -- 완료건수 (검사, 보류 제외)
        SUM(
            CASE
                WHEN TRIM(COALESCE(progress, '')) NOT IN ('검사', '보류')
                THEN 1
                ELSE 0
            END
        ) AS completed_cnt,

        SUM(
            CASE
                WHEN TRIM(COALESCE(issue,'')) NOT IN ('','없음')
                THEN 1
                ELSE 0
            END
        ) AS issues,

        ROUND(
            SUM(COALESCE(actual_hours,0)),
            1
        ) AS hours,

        SUM(
            COALESCE(headcount,0)
        ) AS workers

    FROM YDP

    GROUP BY
        ship_no,
        block_no

    ORDER BY
        ship_no,
        block_no
    """

    return fetch_dataframe(query)

##########################################################################