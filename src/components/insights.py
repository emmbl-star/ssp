import streamlit as st
from utils.add_info_nof import add_info, EnrichRequest
from src.components.ui import info_box, sources_list

_BLUE = "{_BLUE}"


def render_insights(payload: dict, result: dict):
    st.divider()
    st.subheader("Company insights")

    with st.spinner("Fetching insights..."):
        req = EnrichRequest(
            company=payload["company_name"],
            success=1 if result["predicted_class"] == "Operating" else 0,
            probability=int(result["confidence"] * 100),
        )
        insights = add_info(req)

    overview_tab, funding_tab, momentum_tab, industry_tab, peers_tab, drivers_tab, recs_tab, summary_tab = st.tabs([
        "Overview", "Funding", "Momentum", "Industry",
        "Peers", "Drivers & Risks", "Recommendations", "Investor Summary",
    ])

    with overview_tab:
        basics = insights["basics"]
        h = req.probability  # success score out of 100, reusable across tabs

        st.markdown(
            f"""
            <div style="display:flex;align-items:flex-start;gap:2rem;margin-bottom:1.25rem">
              <div style="min-width:140px;margin:0;padding:0">
                <p style="font-size:0.78rem;font-weight:600;text-transform:uppercase;
                          letter-spacing:0.06em;color:gray;margin:0;padding:0;line-height:1.3">
                  Success<br>Probability
                </p>
                <p style="font-size:2.8rem;font-weight:700;line-height:1;margin:0.25rem 0 0 0">
                  {h}<span style="font-size:1rem;font-weight:400;color:gray"> / 100</span>
                </p>
              </div>
              <div style="border-left:1px solid #e0e0e0;padding-left:2rem;margin:0;padding-top:0">
                <p style="margin:0 0 0.4rem 0"><strong>Founded:</strong> {basics['founded_year']}</p>
                <p style="margin:0 0 0.4rem 0"><strong>HQ:</strong> {basics['headquarters']}</p>
                <p style="margin:0 0 0.4rem 0"><strong>Industry:</strong> {basics['industry']}</p>
                <p style="margin:0"><strong>Employees:</strong> {basics['employee_count']}</p>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        info_box(basics["summary"])

    with funding_tab:
        f = insights["funding"]
        st.markdown(
            f"- **Total Funding:** {f['total_funding']}\n"
            f"- **Largest Round:** {f['largest_round']}\n"
            f"- **Rounds:** {f['round_count']}\n"
            f"- **Investors:** {f['investor_count']}"
        )

    with momentum_tab:
        m = insights["momentum"]
        st.markdown(
            f"- **News Volume:** {m['news_volume']}\n"
            f"- **Sentiment:** {m['news_sentiment']}\n"
            f"- **Hiring Trend:** {m['hiring_trend']}\n"
            f"- **Product Activity:** {m['product_activity']}"
        )

    with industry_tab:
        ind = insights["industry_comparison"]
        st.markdown(
            f"- **Industry:** {ind['industry']}\n"
            f"- **Avg Funding:** {ind['avg_funding']}\n"
            f"- **Avg Employees:** {ind['avg_employee_count']}\n"
            f"- **Funding position:** {ind['company_vs_industry']['funding_position']}\n"
            f"- **Employee position:** {ind['company_vs_industry']['employee_position']}\n"
            f"- **Momentum position:** {ind['company_vs_industry']['momentum_position']}"
        )

    with peers_tab:
        st.markdown(f'<p style="color:{_BLUE}">{insights["peer_analysis_text"]}</p>', unsafe_allow_html=True)
        st.write("")
        peers = insights["peer_companies"]
        cols = st.columns(len(peers) if peers else 1)
        for col, peer in zip(cols, peers):
            with col:
                st.markdown(
                    f"**{peer['name']}**\n"
                    f"- Funding: {peer['funding']}\n"
                    f"- Employees: {peer['employee_count']}\n"
                    f"- Momentum: {peer['momentum']}"
                )

    with drivers_tab:
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Drivers**")
            st.markdown("\n".join(f"- {d}" for d in insights["drivers"]))
        with col2:
            st.markdown("**Risks**")
            st.markdown("\n".join(f"- {r}" for r in insights["risks"]))

    with recs_tab:
        st.markdown("\n".join(f"- {rec}" for rec in insights["recommendations"]))

    with summary_tab:
        st.markdown(f'<p style="color:{_BLUE}">{insights["investor_viability_text"]}</p>', unsafe_allow_html=True)

    sources_list(insights.get("sources", []))
