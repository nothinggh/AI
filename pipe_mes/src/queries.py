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
def bom_summary_by_ship():
    return fetch_dataframe("""
        SELECT 
            ship_no,
            SUM(quantity) AS total_quantity,
            ROUND(SUM(weight), 2) AS total_weight,
            SUM(price * quantity) AS total_price
        FROM BOM
        GROUP BY ship_no
        ORDER BY ship_no
        """)


# 2. 특정 호선(ship_no)의 BOM 데이터만 조회하는 함수
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
