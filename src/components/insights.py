import streamlit as st
from utils.add_info_nof import add_info, EnrichRequest


def render_insights(payload: dict, result: dict):
    st.divider()
    st.subheader("📊 Company Insights")

    with st.spinner("Fetching insights..."):
        req = EnrichRequest(
            company=payload["company_name"],
            success=1 if result["success_probability"] >= 0.5 else 0,
            probability=int(result["success_probability"] * 100),
        )
        insights = add_info(req)

    overview_tab, funding_tab, momentum_tab, industry_tab, peers_tab, drivers_tab, recs_tab, summary_tab = st.tabs([
        "Overview", "Funding", "Momentum", "Industry",
        "Peers", "Drivers & Risks", "Recommendations", "Investor Summary",
    ])

    with overview_tab:
        basics = insights["basics"]
        col1, col2 = st.columns(2)
        col1.metric("Success Probability", f"{req.probability}%")
        col2.progress(req.probability / 100)
        st.markdown(f"**Founded:** {basics['founded_year']}  \n**HQ:** {basics['headquarters']}  \n**Industry:** {basics['industry']}  \n**Employees:** {basics['employee_count']}")
        st.info(basics["summary"])

    with funding_tab:
        f = insights["funding"]
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total Funding", f["total_funding"])
        c2.metric("Largest Round", f["largest_round"])
        c3.metric("Rounds", f["round_count"])
        c4.metric("Investors", f["investor_count"])

    with momentum_tab:
        m = insights["momentum"]
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("News Volume", m["news_volume"])
        c2.metric("Sentiment", m["news_sentiment"])
        c3.metric("Hiring Trend", m["hiring_trend"])
        c4.metric("Product Activity", m["product_activity"])

    with industry_tab:
        ind = insights["industry_comparison"]
        st.markdown(f"**Industry:** {ind['industry']}  \n**Avg Funding:** {ind['avg_funding']}  \n**Avg Employees:** {ind['avg_employee_count']}")
        st.success(f"Funding position: {ind['company_vs_industry']['funding_position']}")
        st.success(f"Employee position: {ind['company_vs_industry']['employee_position']}")
        st.success(f"Momentum position: {ind['company_vs_industry']['momentum_position']}")

    with peers_tab:
        for peer in insights["peer_companies"]:
            with st.expander(peer["name"]):
                st.write(f"Funding: {peer['funding']}  |  Employees: {peer['employee_count']}  |  Momentum: {peer['momentum']}")
        st.info(insights["peer_analysis_text"])

    with drivers_tab:
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("### Drivers")
            for d in insights["drivers"]:
                st.success(f"• {d}")
        with col2:
            st.markdown("### Risks")
            for r in insights["risks"]:
                st.error(f"• {r}")

    with recs_tab:
        for rec in insights["recommendations"]:
            st.warning(f"• {rec}")

    with summary_tab:
        st.write(insights["investor_viability_text"])
