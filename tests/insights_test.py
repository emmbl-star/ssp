import streamlit as st
import uuid
from utils.add_info import add_info, EnrichRequest

# -------------------------------------------------------------
# PAGE CONFIGURATION
# -------------------------------------------------------------
st.set_page_config(
    page_title="Startup Insights Tester",
    layout="wide",
    page_icon="📊"
)

st.title("📊 Startup Insights Tester")

# -------------------------------------------------------------
# SESSION STATE INITIALIZATION
# -------------------------------------------------------------
if "insights" not in st.session_state:
    st.session_state.insights = None

if "trigger" not in st.session_state:
    st.session_state.trigger = None

if "last_company" not in st.session_state:
    st.session_state.last_company = None

# -------------------------------------------------------------
# MANUAL INPUTS
# -------------------------------------------------------------
st.subheader("📥 Input Parameters")

company = st.text_input("Company Name", "OpenAI")
success_input = st.selectbox("Success Classification (0 = fail, 1 = succeed)", [0, 1])
probability_input = st.slider("Success Probability (%)", 0, 100, 75)

# -------------------------------------------------------------
# CLEAR INSIGHTS WHEN COMPANY CHANGES
# -------------------------------------------------------------
if st.session_state.last_company != company:
    st.session_state.insights = None
    st.session_state.trigger = uuid.uuid4()
st.session_state.last_company = company

# -------------------------------------------------------------
# BUTTON TO GENERATE INSIGHTS
# -------------------------------------------------------------
if st.button("Generate Insights"):
    try:
        req = EnrichRequest(company=company, success=success_input, probability=probability_input)
        st.session_state.insights = add_info(req)
        st.session_state.trigger = uuid.uuid4()
        st.success("Insights generated successfully!")
    except Exception as e:
        st.error(f"❌ Failed to generate insights: {e}")
        st.stop()

# -------------------------------------------------------------
# GUARD: NO INSIGHTS YET
# -------------------------------------------------------------
if st.session_state.insights is None:
    st.info("Enter parameters and click **Generate Insights** to view insights.")
    st.stop()

# -------------------------------------------------------------
# LOAD FRESH DATA
# -------------------------------------------------------------
data = st.session_state.insights

# -------------------------------------------------------------
# TABS FOR CLEAN NAVIGATION
# -------------------------------------------------------------
overview_tab, funding_tab, momentum_tab, industry_tab, peers_tab, drivers_tab, recs_tab, summary_tab = st.tabs([
    "Overview",
    "Funding",
    "Momentum",
    "Industry Comparison",
    "Peer Companies",
    "Drivers & Risks",
    "Recommendations",
    "Investor Summary"
])

# -------------------------------------------------------------
# OVERVIEW TAB
# -------------------------------------------------------------
with overview_tab:
    st.header(f"🏢 Company Overview — {company}")

    col1, col2 = st.columns([1, 1])
    with col1:
        st.metric(
            label="Success Classification",
            value="Likely Success" if data["success"] == 1 else "Likely Failure",
            delta=f"{data['probability']}% probability"
        )
    with col2:
        st.progress(data["probability"] / 100)

    basics = data["basics"]
    st.markdown(f"""
    **Founded:** {basics['founded_year']}
    **Headquarters:** {basics['headquarters']}
    **Industry:** {basics['industry']}
    **Employees:** {basics['employee_count']}
    """)
    st.info(basics["summary"])

# -------------------------------------------------------------
# FUNDING TAB
# -------------------------------------------------------------
with funding_tab:
    st.header("💰 Funding Overview")
    funding = data["funding"]

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Funding", funding["total_funding"])
    col2.metric("Largest Round", funding["largest_round"])
    col3.metric("Funding Rounds", funding["round_count"])
    col4.metric("Investor Count", funding["investor_count"])

# -------------------------------------------------------------
# MOMENTUM TAB
# -------------------------------------------------------------
with momentum_tab:
    st.header("📈 Market Momentum")
    momentum = data["momentum"]

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("News Volume", momentum["news_volume"])
    col2.metric("Sentiment", momentum["news_sentiment"])
    col3.metric("Hiring Trend", momentum["hiring_trend"])
    col4.metric("Product Activity", momentum["product_activity"])

# -------------------------------------------------------------
# INDUSTRY COMPARISON TAB
# -------------------------------------------------------------
with industry_tab:
    st.header("🏭 Industry Comparison")
    industry = data["industry_comparison"]

    st.markdown(f"""
    **Industry:** {industry['industry']}
    **Avg Funding:** {industry['avg_funding']}
    **Avg Employee Count:** {industry['avg_employee_count']}
    **Avg Momentum:** {industry['avg_momentum']}
    """)

    st.success(f"**Funding Position:** {industry['company_vs_industry']['funding_position']}")
    st.success(f"**Employee Position:** {industry['company_vs_industry']['employee_position']}")
    st.success(f"**Momentum Position:** {industry['company_vs_industry']['momentum_position']}")

# -------------------------------------------------------------
# PEER COMPANIES TAB
# -------------------------------------------------------------
with peers_tab:
    st.header("🤝 Peer Companies")

    for peer in data["peer_companies"]:
        with st.expander(peer["name"]):
            st.write(f"Funding: {peer['funding']}")
            st.write(f"Employees: {peer['employee_count']}")
            st.write(f"Momentum: {peer['momentum']}")

    st.info(data["peer_analysis_text"])

# -------------------------------------------------------------
# DRIVERS & RISKS TAB
# -------------------------------------------------------------
with drivers_tab:
    st.header("⚙️ Key Drivers & 🚨 Risks")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### 🔑 Drivers")
        for d in data["drivers"]:
            st.success(f"• {d}")

    with col2:
        st.markdown("### ⚠️ Risks")
        for r in data["risks"]:
            st.error(f"• {r}")

# -------------------------------------------------------------
# RECOMMENDATIONS TAB
# -------------------------------------------------------------
with recs_tab:
    st.header("🧭 Recommendations")
    for rec in data["recommendations"]:
        st.warning(f"• {rec}")

# -------------------------------------------------------------
# INVESTOR SUMMARY TAB
# -------------------------------------------------------------
with summary_tab:
    st.header("📝 Investor Viability Summary")
    st.write(data["investor_viability_text"])
