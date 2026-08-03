import pandas as pd  # type: ignore
import streamlit as st

from src.queries import (
    bom_summary_by_ship,
    load_drawing_status,
    load_insp_status,
    load_ydp_status,
)

# =====================================================
# PAGE
# =====================================================

st.set_page_config(page_title="PIPE MES 호선 관리", page_icon="🚢", layout="wide")


# =====================================================
# CSS
# =====================================================

st.markdown(
    """
<style>

/* =====================================================
   기본
===================================================== */

.title{
    font-size:34px;
    font-weight:800;
    color:#0f172a;
}


/* =====================================================
   Ship Card
===================================================== */

.ship-card{
    background:#ffffff;
    color:#0f172a;
    border:1px solid #cbd5e1;
    border-radius:18px;
    padding:20px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.08);
}

.total-header-container {
    display: flex;
    justify-content: space-around;
    align-items: center;
    margin-top: 15px;
    text-align: center;
}

.total-item {
    flex: 1;
}

/* =====================================================
   전체 진행률 & 이슈
===================================================== */

.total-progress{
    font-size:48px;
    font-weight:900;
    color:#2563eb;
}

.total-issues{
    font-size:48px;
    font-weight:900;
    color:#dc2626;
}

.total-label {
    font-size: 15px;
    font-weight: 700;
    color: #64748b;
    margin-top: 4px;
}


/* =====================================================
   Process Card
===================================================== */

.process-card{
    color:#0f172a;
    border-radius:15px;
    padding:15px;
    border:1px solid #cbd5e1;
    text-align:center;
}


/* 완료 */

.complete{
    background:#dcfce7;
    border:2px solid #16a34a;
}


/* 진행 */

.running{
    background:#dbeafe;
    border:2px solid #2563eb;
}


/* 이슈 */

.issue{
    background:#fee2e2;
    border:2px solid #dc2626;
}


/* 대기 */

.wait{
    background:#f1f5f9;
    border:2px solid #94a3b8;
}


.value{
    font-size:28px;
    font-weight:900;
}


.rate{
    font-size:22px;
    font-weight:900;
    color:#2563eb;
}



/* =====================================================
   Badge
===================================================== */

.badge{
    display:inline-block;
    padding:7px 12px;
    margin:4px;
    border-radius:20px;
    font-size:13px;
    font-weight:700;
}


.badge-green{
    background:#dcfce7;
    color:#166534;
}


.badge-blue{
    background:#dbeafe;
    color:#1e40af;
}


.badge-red{
    background:#fee2e2;
    color:#991b1b;
}



/* =====================================================
   DARK MODE
===================================================== */


@media (prefers-color-scheme: dark) {


.title{
    color:#f8fafc;
}


.ship-card{
    background:#1e293b;
    color:#f8fafc;
    border:1px solid #475569;
    box-shadow: 0 4px 16px rgba(0,0,0,0.5);
}


.process-card{
    color:#f8fafc;
    border-color:#475569;
}


/* 완료 */

.complete{
    background:#064e3b;
    border-color:#22c55e;
}



/* 진행 */

.running{
    background:#1e3a8a;
    border-color:#3b82f6;
}



/* 이슈 */

.issue{
    background:#7f1d1d;
    border-color:#ef4444;
}



/* 대기 */

.wait{
    background:#334155;
    border-color:#64748b;
}


.rate{
    color:#60a5fa;
}

.total-issues {
    color: #f87171;
}

.total-label {
    color: #94a3b8;
}


/* badge */


.badge-green{
    background:#14532d;
    color:#bbf7d0;
}



.badge-blue{
    background:#1e3a8a;
    color:#bfdbfe;
}



.badge-red{
    background:#7f1d1d;
    color:#fecaca;
}


}

</style>
""",
    unsafe_allow_html=True,
)


# =====================================================
# DATA
# =====================================================

target_hulls = ["SN101", "SN201", "SN301"]


df_bom = bom_summary_by_ship()

df_mfp = load_drawing_status()

df_insp = load_insp_status()

df_ydp = load_ydp_status()


# =====================================================
# FUNCTION
# =====================================================


def rate(done, total):
    if total == 0:
        return 0
    return int(done / total * 100)


def state_class(percent, issues=0):
    if issues > 0:
        return "issue"
    if percent >= 100:
        return "complete"
    if percent > 0:
        return "running"
    return "wait"


def state_icon(percent, issues=0):
    if issues > 0:
        return "🔴"
    if percent >= 100:
        return "🟢"
    if percent > 0:
        return "🔵"
    return "⚪"


# =====================================================
# TITLE
# =====================================================

st.title("📌 주요 지표")

# st.caption("Ship Production Monitoring System")

st.divider()


# =====================================================
# SHIP LOOP
# =====================================================


for ship in target_hulls:

    bom = df_bom[df_bom.ship_no == ship] if not df_bom.empty else pd.DataFrame()
    mfp = df_mfp[df_mfp.ship_no == ship] if not df_mfp.empty else pd.DataFrame()
    insp = df_insp[df_insp.ship_no == ship] if not df_insp.empty else pd.DataFrame()
    ydp = df_ydp[df_ydp.ship_no == ship] if not df_ydp.empty else pd.DataFrame()

    rates = []
    total_issues = 0  # 전체 이슈 건수 변수 초기화

    # ===============================
    # MFP
    # ===============================

    mfp_done = 0
    mfp_total = 0

    if not mfp.empty:
        mfp_done = int(mfp["완료건수"].sum())
        mfp_total = int(mfp["도면건수"].sum())
        if "issues" in mfp.columns:
            total_issues += int(mfp["issues"].sum())

    mfp_rate = rate(mfp_done, mfp_total)
    rates.append(mfp_rate)

    # ===============================
    # INSP
    # ===============================

    insp_done = 0
    insp_total = 0

    if not insp.empty:
        insp_done = int(insp["completed"].sum())
        insp_total = int(insp["cnt"].sum())
        if "issues" in insp.columns:
            total_issues += int(insp["issues"].sum())

    insp_rate = rate(insp_done, insp_total)
    rates.append(insp_rate)

    # ===============================
    # YDP
    # ===============================

    ydp_done = 0
    ydp_total = 0
    ydp_issues = 0

    if not ydp.empty:
        ydp_total = int(ydp["total_cnt"].sum())

        if "issues" in ydp.columns:
            ydp_issues = int(ydp["issues"].sum())
            total_issues += ydp_issues

        if "completed_cnt" in ydp.columns:
            ydp_done = int(ydp["completed_cnt"].sum())
        elif "completed" in ydp.columns:
            ydp_done = int(ydp["completed"].sum())
        else:
            ydp_done = ydp_total - ydp_issues

    ydp_rate = rate(ydp_done, ydp_total)
    rates.append(ydp_rate)

    total_rate = int(sum(rates) / len(rates)) if rates else 0

    # =====================================================
    # HEADER (진행률 및 이슈 건수)
    # =====================================================

    st.markdown(
        f"""
<div class="ship-card">
    <h2>🚢 {ship}</h2>
    <div class="total-header-container">
        <div class="total-item">
            <div class="total-progress">{total_rate}%</div>
            <div class="total-label">전체 진행률</div>
        </div>
        <div style="border-left: 1px solid #cbd5e1; height: 50px;"></div>
        <div class="total-item">
            <div class="total-issues">{total_issues:,}</div>
            <div class="total-label">전체 이슈 건수</div>
        </div>
    </div>
</div>
""",
        unsafe_allow_html=True,
    )

    st.write("")

    cols = st.columns(4)

    # =====================================================
    # BOM
    # =====================================================

    with cols[0]:
        qty = 0
        weight_ton = 0.0

        if not bom.empty:
            qty = int(bom.total_quantity.sum())
            weight_ton = round(bom.total_weight.sum() / 1000, 1)

        st.markdown(
            f"""
<div class="process-card complete">
    <h3>📦 BOM</h3>
    <div class="value">{qty:,} EA</div>
    <div class="rate">{weight_ton:,.1f} ton</div>
    자재 주문
</div>
""",
            unsafe_allow_html=True,
        )

    # =====================================================
    # MFP
    # =====================================================

    with cols[1]:
        st.markdown(
            f"""
<div class="process-card {state_class(mfp_rate)}">
    <h3>🔧 MFP</h3>
    <div class="value">{mfp_done}/{mfp_total}</div>
    <div class="rate">진행률 {mfp_rate}%</div>
    제작 공정
</div>
""",
            unsafe_allow_html=True,
        )

    # =====================================================
    # INSP
    # =====================================================

    with cols[2]:
        st.markdown(
            f"""
<div class="process-card {state_class(insp_rate)}">
    <h3>🔩 INSP</h3>
    <div class="value">{insp_done}/{insp_total}</div>
    <div class="rate">진행률 {insp_rate}%</div>
    설치 공정
</div>
""",
            unsafe_allow_html=True,
        )

    # =====================================================
    # YDP
    # =====================================================

    with cols[3]:
        st.markdown(
            f"""
<div class="process-card {state_class(ydp_rate, ydp_issues)}">
    <h3>🏗 YDP</h3>
    <div class="value">{ydp_done}/{ydp_total}</div>
    <div class="rate">진행률 {ydp_rate}%</div>
    YARD 공정
</div>
""",
            unsafe_allow_html=True,
        )

    # =====================================================
    # BLOCK
    # =====================================================

    st.markdown("### 🧩 BLOCK 현황")

    if not ydp.empty:
        html = ""

        for _, row in ydp.iterrows():
            total = row["total_cnt"]

            if "completed_cnt" in ydp.columns:
                done = row["completed_cnt"]
            elif "completed" in ydp.columns:
                done = row["completed"]
            else:
                done = total - row["issues"]

            p = rate(done, total)
            issue = int(row.get("issues", 0))

            if issue > 0:
                badge = "badge-red"
            elif p >= 100:
                badge = "badge-green"
            else:
                badge = "badge-blue"

            html += f"""
<span class="badge {badge}">
{state_icon(p, issue)}
{row['block_no']}
{p}%
"""

            if issue > 0:
                html += f" ⚠️{issue}"

            html += """
</span>
"""

        st.markdown(html, unsafe_allow_html=True)

    st.divider()