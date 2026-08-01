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


def table_list():
    return fetch_dataframe("""
        SELECT name AS table_name
        FROM sqlite_master
        WHERE type = 'table'
        ORDER BY name
        """)


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
    
    # DB에서 DataFrame으로 조회
    df = fetch_dataframe(query)
    
    # 컬럼명 한글 변경 (필요 시)
    df.columns = ['호선 번호', '제작업체', '도면 갯수', '이슈 건수', '토탈 실투입 시간', '작업자 수', '총 공수(M/H)']
    return df

# 실행 예시
df_result = get_ship_summary_df()
print(df_result)