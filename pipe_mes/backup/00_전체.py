import pandas as pd  # type: ignore
import streamlit as st

st.set_page_config(page_title="전체 현황", layout="wide")

from src.queries import bom_summary_by_ship

st.title("🚢 전체 현황")
st.markdown("---")

df_summary = bom_summary_by_ship()

if isinstance(df_summary, pd.DataFrame) and not df_summary.empty:
    st.subheader("📌 BOM 호선별 집계 현황")
    df_display = df_summary[
        ["ship_no", "total_quantity", "total_weight", "total_price"]
    ]

    st.dataframe(
        df_display,
        column_config={
            "ship_no": st.column_config.TextColumn("호선 번호"),
            "total_quantity": st.column_config.NumberColumn(
                "총수량(EA)", format="%,d"
            ),
            "total_weight": st.column_config.NumberColumn(
                "총중량(kg)", format="%,.2f"
            ),
            "total_price": st.column_config.NumberColumn(
                "총금액(원)", format="%,d"
            ),
        },
        hide_index=True,
        use_container_width=True,
    )

    st.subheader("📊 BOM 호선별 비교 차트")

    c1, c2, c3 = st.columns(3)

    with c1:
        st.caption("호선별 총수량(EA)")
        st.bar_chart(
            data=df_summary,
            x="ship_no",
            y="total_quantity",
            color="#2b5c8f",
            use_container_width=True,
        )

    with c2:
        st.caption("호선별 총중량(kg)")
        st.bar_chart(
            data=df_summary,
            x="ship_no",
            y="total_weight",
            color="#2e7d32",
            use_container_width=True,
        )

    with c3:
        st.caption("호선별 총금액(원)")
        st.bar_chart(
            data=df_summary,
            x="ship_no",
            y="total_price",
            color="#c62828",
            use_container_width=True,
        )

else:
    st.info("조회된 호선 집계 데이터가 없습니다.")

st.markdown("---")