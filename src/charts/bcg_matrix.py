"""
BCG Matrix – Interactive Streamlit App
Inspired by the classic Boston Consulting Group portfolio analysis tool.
"""

import streamlit as st
import plotly.graph_objects as go
import pandas as pd

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="BCG Matrix",
    page_icon="📊",
    layout="wide",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown(
    """
    <style>
      /* Font & base */
      @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
      html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

      /* Header strip */
      .bcg-header {
        background: linear-gradient(135deg, #0d2b55 0%, #1a4a8a 100%);
        padding: 1.4rem 2rem;
        border-radius: 12px;
        margin-bottom: 1.5rem;
        color: #ffffff;
      }
      .bcg-header h1 { margin: 0; font-size: 1.9rem; font-weight: 700; letter-spacing: -0.5px; }
      .bcg-header p  { margin: 0.25rem 0 0; font-size: 0.9rem; opacity: 0.75; }

      /* Quadrant legend cards */
      .quad-card {
        border-radius: 10px;
        padding: 1rem 1.1rem;
        margin-bottom: 0.6rem;
        color: #fff;
      }
      .quad-card h4 { margin: 0 0 0.3rem; font-size: 1rem; font-weight: 700; }
      .quad-card p  { margin: 0; font-size: 0.78rem; line-height: 1.45; opacity: 0.92; }
      .star-card   { background: #2563eb; }
      .cow-card    { background: #16a34a; }
      .qm-card     { background: #9333ea; }
      .dog-card    { background: #dc2626; }

      /* Sidebar tweaks */
      .sidebar .sidebar-content { padding-top: 1rem; }

      /* Table */
      .stDataFrame { border-radius: 10px; overflow: hidden; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown(
    """
    <div class="bcg-header">
      <h1>📊 BCG Matrix</h1>
      <p>Boston Consulting Group · Portfolio Analysis Tool</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ── Session-state for products ────────────────────────────────────────────────
DEMO_PRODUCTS = [
    {"name": "Product A", "market_share": 75, "growth_rate": 22, "revenue": 120},
    {"name": "Product B", "market_share": 80, "growth_rate": 8,  "revenue": 200},
    {"name": "Product C", "market_share": 25, "growth_rate": 18, "revenue": 60},
    {"name": "Product D", "market_share": 20, "growth_rate": 5,  "revenue": 40},
    {"name": "Product E", "market_share": 60, "growth_rate": 25, "revenue": 90},
    {"name": "Product F", "market_share": 15, "growth_rate": 3,  "revenue": 30},
]

if "products" not in st.session_state:
    st.session_state.products = DEMO_PRODUCTS.copy()

# ── Sidebar – Add / manage products ──────────────────────────────────────────
with st.sidebar:
    st.markdown("### ➕ Add a Product")
    with st.form("add_product", clear_on_submit=True):
        p_name   = st.text_input("Product name", placeholder="e.g. Product G")
        p_share  = st.slider("Relative Market Share (%)", 1, 100, 50,
                             help="Higher = stronger competitive position")
        p_growth = st.slider("Market Growth Rate (%)", 0, 40, 10,
                             help="Growth rate of the market segment")
        p_rev    = st.number_input("Annual Revenue ($M)", min_value=1, max_value=1000,
                                   value=50, step=5)
        submitted = st.form_submit_button("Add Product", use_container_width=True)
        if submitted and p_name.strip():
            st.session_state.products.append({
                "name": p_name.strip(),
                "market_share": p_share,
                "growth_rate":  p_growth,
                "revenue":      p_rev,
            })
            st.success(f"✅ '{p_name}' added!")

    st.divider()
    st.markdown("### 🗂 Manage Products")
    if st.session_state.products:
        names_to_remove = st.multiselect(
            "Remove products",
            [p["name"] for p in st.session_state.products],
        )
        if st.button("Remove selected", use_container_width=True) and names_to_remove:
            st.session_state.products = [
                p for p in st.session_state.products
                if p["name"] not in names_to_remove
            ]
            st.rerun()
    if st.button("🔄 Reset to demo data", use_container_width=True):
        st.session_state.products = DEMO_PRODUCTS.copy()
        st.rerun()

    st.divider()
    st.markdown("### ⚙️ Axis Thresholds")
    share_thresh  = st.slider("Market Share threshold (%)",  10, 90, 50)
    growth_thresh = st.slider("Growth Rate threshold (%)",    1, 30, 10)


# ── Helper: classify ─────────────────────────────────────────────────────────
QUADRANT_COLORS = {
    "⭐ Star":          "#2563eb",
    "🐄 Cash Cow":     "#16a34a",
    "❓ Question Mark": "#9333ea",
    "🐕 Dog":           "#dc2626",
}

def classify(share, growth, st_thresh, gr_thresh):
    high_share  = share  >= st_thresh
    high_growth = growth >= gr_thresh
    if   high_share and high_growth:  return "⭐ Star"
    elif high_share and not high_growth: return "🐄 Cash Cow"
    elif not high_share and high_growth: return "❓ Question Mark"
    else:                              return "🐕 Dog"


products = st.session_state.products
df = pd.DataFrame(products)
if df.empty:
    st.info("Add some products using the sidebar to get started.")
    st.stop()

df["quadrant"] = df.apply(
    lambda r: classify(r.market_share, r.growth_rate, share_thresh, growth_thresh),
    axis=1,
)
df["color"] = df["quadrant"].map(QUADRANT_COLORS)

# ── Layout: chart + legend ────────────────────────────────────────────────────
chart_col, legend_col = st.columns([3, 1])

with chart_col:
    fig = go.Figure()

    # Quadrant shading
    def quad_bg(x0, x1, y0, y1, color, label):
        fig.add_shape(type="rect", x0=x0, x1=x1, y0=y0, y1=y1,
                      fillcolor=color, opacity=0.08, line_width=0)
        fig.add_annotation(x=(x0+x1)/2, y=(y0+y1)/2, text=label,
                           font=dict(size=13, color=color, family="Inter"),
                           showarrow=False, opacity=0.35)

    x_max = 105
    y_max = max(df.growth_rate.max() * 1.2, growth_thresh * 2.2, 35)

    quad_bg(share_thresh, x_max, growth_thresh, y_max, "#2563eb", "⭐ STARS")
    quad_bg(0,            share_thresh, growth_thresh, y_max, "#9333ea", "❓ QUESTION MARKS")
    quad_bg(share_thresh, x_max, 0,            growth_thresh, "#16a34a", "🐄 CASH COWS")
    quad_bg(0,            share_thresh, 0,            growth_thresh, "#dc2626", "🐕 DOGS")

    # Threshold lines
    fig.add_vline(x=share_thresh,  line_dash="dash", line_color="#6b7280", line_width=1.5)
    fig.add_hline(y=growth_thresh, line_dash="dash", line_color="#6b7280", line_width=1.5)

    # Bubbles by quadrant group
    for quad, color in QUADRANT_COLORS.items():
        sub = df[df["quadrant"] == quad]
        if sub.empty:
            continue
        fig.add_trace(go.Scatter(
            x=sub["market_share"],
            y=sub["growth_rate"],
            mode="markers+text",
            name=quad,
            text=sub["name"],
            textposition="top center",
            textfont=dict(size=11, family="Inter", color="#111827"),
            marker=dict(
                size=sub["revenue"] ** 0.5 * 3.5,   # bubble size ~ sqrt(revenue)
                color=color,
                opacity=0.85,
                line=dict(color="#ffffff", width=2),
            ),
            customdata=sub[["revenue", "quadrant"]].values,
            hovertemplate=(
                "<b>%{text}</b><br>"
                "Market Share: %{x}%<br>"
                "Growth Rate:  %{y}%<br>"
                "Revenue: $%{customdata[0]}M<br>"
                "Quadrant: %{customdata[1]}"
                "<extra></extra>"
            ),
        ))

    fig.update_layout(
        title=dict(text="Product Portfolio — BCG Matrix", font=dict(size=16, family="Inter")),
        xaxis=dict(
            title="Relative Market Share (%)",
            range=[0, x_max],
            gridcolor="#e5e7eb",
            zeroline=False,
        ),
        yaxis=dict(
            title="Market Growth Rate (%)",
            range=[0, y_max],
            gridcolor="#e5e7eb",
            zeroline=False,
        ),
        legend=dict(orientation="h", y=-0.18, x=0.5, xanchor="center",
                    font=dict(size=11)),
        paper_bgcolor="white",
        plot_bgcolor="#fafafa",
        margin=dict(l=60, r=30, t=60, b=100),
        height=520,
    )

    st.plotly_chart(fig, use_container_width=True)
    st.caption("💡 Bubble size represents annual revenue. Drag to zoom, hover for details.")

with legend_col:
    st.markdown("#### Quadrant Guide")
    st.markdown("""
    <div class="quad-card star-card">
      <h4>⭐ Stars</h4>
      <p>High share · High growth. Market leaders — invest to maintain position.</p>
    </div>
    <div class="quad-card cow-card">
      <h4>🐄 Cash Cows</h4>
      <p>High share · Low growth. Mature leaders — milk for cash to fund others.</p>
    </div>
    <div class="quad-card qm-card">
      <h4>❓ Question Marks</h4>
      <p>Low share · High growth. Uncertain — invest selectively or divest.</p>
    </div>
    <div class="quad-card dog-card">
      <h4>🐕 Dogs</h4>
      <p>Low share · Low growth. Weak position — phase out or reposition.</p>
    </div>
    """, unsafe_allow_html=True)

# ── Summary metrics ───────────────────────────────────────────────────────────
st.divider()
counts = df["quadrant"].value_counts()
m1, m2, m3, m4 = st.columns(4)
for col, quad, emoji in [
    (m1, "⭐ Star",           "⭐"),
    (m2, "🐄 Cash Cow",      "🐄"),
    (m3, "❓ Question Mark",  "❓"),
    (m4, "🐕 Dog",            "🐕"),
]:
    n   = counts.get(quad, 0)
    rev = df[df["quadrant"] == quad]["revenue"].sum()
    col.metric(f"{quad}", f"{n} products", f"${rev}M revenue")

# ── Data table ────────────────────────────────────────────────────────────────
st.divider()
st.markdown("#### 📋 Product Details")
display_df = df[["name", "market_share", "growth_rate", "revenue", "quadrant"]].copy()
display_df.columns = ["Product", "Market Share (%)", "Growth Rate (%)", "Revenue ($M)", "Quadrant"]
st.dataframe(
    display_df.style.applymap(
        lambda v: f"color: {QUADRANT_COLORS.get(v, '#111')}; font-weight: 600;"
        if v in QUADRANT_COLORS else "",
        subset=["Quadrant"],
    ),
    use_container_width=True,
    hide_index=True,
)

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown(
    "<p style='text-align:center;color:#9ca3af;font-size:0.78rem;margin-top:2rem'>"
    "BCG Matrix · Strategic Portfolio Analysis · Built with Streamlit & Plotly</p>",
    unsafe_allow_html=True,
)
