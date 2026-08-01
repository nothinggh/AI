from src.db import fetch_all, fetch_dataframe, fetch_one

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


# 1. 호선별 자재 집계 함수 (총수량/총중량/총금액)
def bom_summary_by_ship(keyword: str = ""):
    """호선(ship_no)별 BOM 총수량, 총중량, 총금액을 집계합니다."""
    where = ["ship_no IS NOT NULL AND ship_no != ''"]
    params = []

    if keyword:
        where.append("ship_no LIKE ?")
        params.append(f"%{keyword}%")

    where_clause = " AND ".join(where)

    # Note: price가 단가라면 SUM(price * quantity)로 수정하세요.
    # 만약 price가 이미 해당 행의 총금액이라면 SUM(price)가 맞습니다.
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


# 2. 품목(item_type)별 집계 함수 (GROUP BY 수리)
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


# 3. 특정 호선(ship_no)의 BOM 데이터만 조회하는 함수
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