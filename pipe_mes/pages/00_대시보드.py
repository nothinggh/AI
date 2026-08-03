import pandas as pd  # type: ignore
import streamlit as st
import plotly.express as px  # type: ignore

st.set_page_config(page_title="주요 지표", layout="wide")

from src.queries import (
    table_counts,
    bom_summary_by_ship,
    load_drawing_status,
    load_insp_status,
    load_ydp_status,
)

st.title("📌 주요 지표")
st.markdown("---")
st.subheader("📋 DB테이블명(품목수)")
df_counts = table_counts()
counts_dict = dict(zip(df_counts["table_name"], df_counts["row_count"]))
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric(label="BOM", value=f"{counts_dict.get('BOM', 0):,} 건")
with col2:
    st.metric(label="MFP", value=f"{counts_dict.get('MFP', 0):,} 건")
with col3:
    st.metric(label="INSP", value=f"{counts_dict.get('INSP', 0):,} 건")
with col4:
    st.metric(label="YDP", value=f"{counts_dict.get('YDP', 0):,} 건")

##########################################################################

st.markdown("---")
df_summary = bom_summary_by_ship()
if isinstance(df_summary, pd.DataFrame) and not df_summary.empty:
    st.subheader("📦 자재 주문(BOM) 현황")
    df_display = df_summary[
        ["ship_no", "total_quantity", "total_weight", "total_price"]
    ]

    st.dataframe(
        df_display,
        column_config={
            "ship_no": st.column_config.TextColumn("호선 번호"),
            "total_quantity": st.column_config.NumberColumn("총수량(EA)", format="%,d"),
            "total_weight": st.column_config.NumberColumn("총중량(kg)", format="%,.2f"),
            "total_price": st.column_config.NumberColumn("총금액(원)", format="%,d"),
        },
        hide_index=True,
        use_container_width=True,
    )

    st.markdown("- 차트")

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

##########################################################################

st.subheader("📐 제작 공정(MFP) 현황")

# 데이터 조회
df = load_drawing_status()

if df.empty:
    st.info("조회된 데이터가 없습니다.")
    st.stop()

# 호선별 Metric 표시
cols_per_row = 4

for i in range(0, len(df), cols_per_row):
    cols = st.columns(cols_per_row)

    for col, (_, row) in zip(cols, df.iloc[i : i + cols_per_row].iterrows()):

        progress = (
            round(row["완료건수"] / row["도면건수"] * 100) if row["도면건수"] > 0 else 0
        )

        with col:
            st.metric(
                label=f"🚢 {row['ship_no']}",
                value=f"{progress}%",
                delta=f"완료 {row['완료건수']} / {row['도면건수']}",
            )

            st.caption(
                f"상태: {row['진행상황']} | "
                f"이슈: {row['이슈건수']}건"
                # /"작업자: {row['작업자']}"
            )
st.markdown("---")

##########################################################################

st.subheader("🔩 설치 공정(INSP) 현황")

df = load_insp_status()

target_hulls = ["SN101", "SN201", "SN301"]

cols = st.columns(len(target_hulls))


for col, ship_no in zip(cols, target_hulls):

    with col:

        st.markdown(f"🚢 {ship_no}")

        ship_df = df[df["ship_no"] == ship_no]

        # 데이터 없는 호선
        if ship_df.empty:

            st.metric(label="상태", value="작업 전", delta="등록 없음")

            continue

        # 호선 전체 집계
        total_cnt = ship_df["cnt"].sum()
        complete_cnt = ship_df["completed"].sum()
        total_issue = ship_df["issues"].sum()

        progress = int(complete_cnt / total_cnt * 100)

        status = "완료" if progress == 100 else "진행중"

        # 진행률 표시
        st.metric(label="진행률", value=f"{progress}%", delta=status)

        # UNIT 수량
        unit_count = (
            ship_df["unit_no"]
            .dropna()
            .astype(str)
            .str.strip()
            .replace("", None)
            .nunique()
        )


st.caption(f"""
UNIT : {unit_count}개 |
배관 : {int(complete_cnt)}/{int(total_cnt)} |
이슈 : {int(total_issue)} 건
""")
st.markdown("---")

##########################################################################

st.subheader("🏗️ YDP 공정(YDP) 현황")

df = load_ydp_status()

target_hulls = ["SN101", "SN201", "SN301"]


for ship_no in target_hulls:

    st.markdown(f"### 🚢 {ship_no}")

    ship_df = df[df["ship_no"] == ship_no]


    if ship_df.empty:

        st.markdown("⏳ 작업 전")
        st.divider()

        continue


    # 전체 수량 / 완료 / 이슈
    total_cnt = ship_df["total_cnt"].sum()
    completed_cnt = ship_df["completed_cnt"].sum()
    total_issue = ship_df["issues"].sum()

    # BLOCK 중복 제거 후 수량
    total_block = (
        ship_df["block_no"]
        .dropna()
        .astype(str)
        .str.strip()
        .nunique()
    )

    # 전체 진행률
    total_progress = round(
        (completed_cnt / total_cnt) * 100
        if total_cnt > 0 else 0
    )


    # BLOCK별 문자열 생성
    block_text = []

    for _, row in ship_df.iterrows():

        progress = round(
            (row["completed_cnt"] / row["total_cnt"]) * 100
            if row["total_cnt"] > 0
            else 0
        )

        block_text.append(
            f"🧩 {row['block_no']} {progress}% (이슈 {int(row['issues'])})"
        )


    st.markdown(
        f"""
<div style="font-size:22px; font-weight:bold;">
    총 진행률 {total_progress}% 
    | 총 이슈 {int(total_issue)}건
    | 총 BLOCK {total_block}개
</div>

<div style="font-size:14px; margin-top:8px;">
    {" | ".join(block_text)}
</div>
""",
        unsafe_allow_html=True,
    )

    st.divider()

###########################################################################