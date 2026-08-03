import streamlit as st

from src.ui import (
    setup_page,
    page_title,
    show_database_status,
)


# =====================================================
# PAGE SETUP
# =====================================================

st.set_page_config(layout="wide")
#     page_title="PIPE MES 소개",
#     page_icon="🚢",
#     layout="wide"
# )

setup_page("소개")


# =====================================================
# TITLE
# =====================================================

# page_title(
#     "배관 관리 시스템")
#     "(Piping Manufacturing Execution System)",
#     "BOM  →  MFP  →  INSP  →  YDP"
# )

# show_database_status()

st.title("🚢 배관 관리 시스템(PMES)")

# =====================================================
# CUSTOM CSS
# =====================================================

st.markdown(
"""
<link rel="stylesheet"
href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">


<style>


/* ================================
   Global
================================ */

.hero-box {

    background: linear-gradient(
        135deg,
        rgba(30,136,229,0.15),
        rgba(66,165,245,0.05)
    );

    border-radius:18px;

    padding:30px;

    margin-bottom:30px;

    text-align:center;

}



.hero-title {

    font-size:34px;

    font-weight:800;

    color:#1976D2;

}



.hero-desc {

    font-size:18px;

    margin-top:12px;

}



.dark-text {

    color:var(--text-color);

}



/* ================================
 Step Card
================================ */


.step-card {


    background:var(--background-color);

    border-radius:18px;

    border:1px solid var(--border-color);


    padding:28px 18px;


    height:260px;


    text-align:center;


    transition:0.25s;


}



.step-card:hover {

    transform:translateY(-8px);

    box-shadow:
    0 12px 30px rgba(0,0,0,0.15);

}



/* badge */

.step-badge {


    display:inline-block;


    padding:6px 18px;


    border-radius:20px;


    background:#1976D2;


    color:white;


    font-weight:700;


    font-size:14px;


}



/* icon */

.step-icon {


    font-size:65px;


    margin:20px 0;


}



.step-title {


    font-size:24px;


    font-weight:800;


}



.step-desc {


    margin-top:10px;


    font-size:15px;


    color:#666;


}





/* Arrow */


.arrow {


    height:260px;


    display:flex;


    justify-content:center;


    align-items:center;


    font-size:35px;


    color:#90A4AE;


}




/* Detail box */


.detail-box {


    background:rgba(128,128,128,0.08);


    padding:20px;


    border-radius:15px;


    margin-top:10px;


    line-height:1.8;


}



</style>


""",
unsafe_allow_html=True
)



# =====================================================
# HERO SECTION
# =====================================================


st.markdown(
"""
<div class="hero-box">

<div class="hero-title">
PMES (Piping Manufacturing Execution System)
</div>


<div class="hero-desc">

배관 자재부터 제작 · 검사 · 현장 설치까지  
전 공정 실시간 관리하는 시스템

</div>


</div>

""",
unsafe_allow_html=True
)



# =====================================================
# PURPOSE
# =====================================================


st.subheader("🎯 개발 목적")


purpose_col = st.columns(4)


purpose_data = [

("📦",
"자재 관리",
"자재 입고 및 BOM 실시간 관리"),

("🏭",
"공정 추적",
"제작 및 설치 진행 현황 관리"),

("⚠️",
"품질 관리",
"이슈 및 불량률 최소화"),

("👷",
"현장 역량",
"작업 효율 향상 및 생산성 개선"),

]


for col,data in zip(purpose_col,purpose_data):

    with col:

        st.info(
            f"""
            **{data[0]} {data[1]}**

            {data[2]}
            """
        )



st.divider()



# =====================================================
# PROCESS FLOW
# =====================================================


st.subheader("⚙️ 배관 작업 프로세스")


steps = [

{
"code":"STEP 01",
"name":"BOM",
"desc":"자재 구매 및 관리",
"icon":"fa-solid fa-boxes-stacked"
},


{
"code":"STEP 02",
"name":"MFP",
"desc":"배관 제작 공정",
"icon":"fa-solid fa-industry"
},


{
"code":"STEP 03",
"name":"INSP",
"desc":"배관 GROUP 구성",
"icon":"fa-solid fa-layer-group"
},


{
"code":"STEP 04",
"name":"YDP",
"desc":"조선소 현장 설치",
"icon":"fa-solid fa-ship"
},

]



cols = st.columns(
    [3,1,3,1,3,1,3]
)



for i,step in enumerate(steps):


    idx=i*2


    with cols[idx]:


        st.markdown(
        f"""
        <div class="step-card">


        <div class="step-badge">
        {step['code']}
        </div>


        <div class="step-icon">

        <i class="{step['icon']}"></i>

        </div>


        <div class="step-title">

        {step['name']}

        </div>


        <div class="step-desc">

        {step['desc']}

        </div>


        </div>

        """,
        unsafe_allow_html=True
        )



    if i < 3:

        with cols[idx+1]:

            st.markdown(
            """
            <div class="arrow">

            <i class="fa-solid fa-arrow-right"></i>

            </div>

            """,
            unsafe_allow_html=True
            )





# =====================================================
# DETAIL
# =====================================================


st.markdown("<br>",unsafe_allow_html=True)


with st.expander(
    "📘 공정별 상세 설명 보기",
    expanded=False
):

    st.markdown(
    """
<b>1. BOM (Bill Of Material) : 필요 배관 자재 산출 및 구매 단계</b><br>
<b>2. MFP (Manufacturing Process) : PIPE 절단, 용접, 벤딩 등 제작 단계</b><br>
<b>3. INSP (Inspection Process) : 개별 배관 UNIT GROUP화 단계</b><br>
<b>4. YDP (Yard Delivery Process) : GROUP 완료된 배관 BLOCK 설치 및 DOCK 최종 탑제 단계</b>
    """,
    unsafe_allow_html=True
    )
