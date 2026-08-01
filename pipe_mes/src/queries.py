from src.db import fetch_all, fetch_dataframe, fetch_one
<<<<<<< HEAD
=======

>>>>>>> 4ab6ebfdddb4234cd8281af0592c71ba3f50ba74

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



<<<<<<< HEAD
# 1. 호선별 자재 집계 함수 (총수량/총중량/총금액)
def bom_summary_by_ship():
=======
    if keyword:
        where.append("(i.item_code LIKE ? OR i.item_name LIKE ?)")
        params.extend([f"%{keyword}%", f"%{keyword}%"])

    if item_type != "전체":
        where.append("i.item_type = ?")
        params.append(item_type)

    return fetch_dataframe(
        f"""
        SELECT
            i.item_id,
            i.item_code,
            i.item_name,
            i.item_type,
            i.unit,
            i.is_active,
            COUNT(DISTINCT l.lot_id) AS lot_count,
            COUNT(DISTINCT pm.production_material_id) AS material_use_count
        FROM (
            SELECT * FROM BOM
            UNION ALL
            SELECT * FROM MFP
            UNION ALL
            SELECT * FROM INSP
            UNION ALL
            SELECT * FROM YDP
        ) AS i
        LEFT JOIN lot AS l
            ON i.item_id = l.item_id
        LEFT JOIN production_material AS pm
            ON i.item_id = pm.material_item_id
        WHERE {' AND '.join(where)}
        GROUP BY
            i.item_id,
            i.item_code,
            i.item_name,
            i.item_type,
            i.unit,
            i.is_active
        ORDER BY i.item_type, i.item_code
        """,
        tuple(params),
    )


def item_type_counts():
>>>>>>> 4ab6ebfdddb4234cd8281af0592c71ba3f50ba74
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
