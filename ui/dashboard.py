import streamlit as st
import plotly.graph_objects as go
from datetime import datetime
from agent.market_data import fetch_current_prices, fetch_historical_data


def render_prices(prices):
    cols = st.columns(len(prices))
    for i, (key, data) in enumerate(prices.items()):
        with cols[i]:
            arrow = "▲" if data["change_1d"] >= 0 else "▼"
            c = "#3fb950" if data["change_1d"] >= 0 else "#f85149"
            st.metric(
                label=f"{data['name']}",
                value=f"${data['price']:,.2f}",
                delta=f"{arrow} {data['change_1d']:+.2f}%",
                delta_color="normal",
            )


def render_charts():
    hist_data = fetch_historical_data("1mo")
    if not hist_data:
        st.info("Donnees historiques non disponibles")
        return
    tabs = st.tabs(list(hist_data.keys()))
    for i, (key, df) in enumerate(hist_data.items()):
        with tabs[i]:
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=df["Date"], y=df["Close"],
                mode="lines", name=key,
                line=dict(color="#7878ff", width=2),
                fill="tozeroy", fillcolor="rgba(120,120,255,0.08)",
            ))
            fig.update_layout(
                title=f"{key} - 30 jours",
                xaxis_title="", yaxis_title="Prix ($)",
                height=380,
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#7878a0", size=11),
                xaxis=dict(gridcolor="#1e1e2e", zeroline=False),
                yaxis=dict(gridcolor="#1e1e2e", zeroline=False),
                margin=dict(l=40, r=20, t=40, b=20),
            )
            st.plotly_chart(fig, use_container_width=True)


def render_daily_brief(brief):
    if not brief:
        st.warning("Brief en cours de generation...")
        return
    st.markdown(f"""<div style="background:linear-gradient(135deg,#15152a,#1a1a35);border:1px solid #2a2a4a;border-radius:12px;padding:12px 16px;margin-bottom:12px;display:flex;justify-content:space-between;align-items:center;">
<span style="color:#f0f0ff;font-weight:600;font-size:14px;">Brief Macro Quotidien</span>
<span style="color:#3a3a5a;font-size:11px;">{datetime.now().strftime('%d/%m/%Y %H:%M')}</span>
</div>""", unsafe_allow_html=True)
    st.markdown(f"""<div style="background:#12121a;border:1px solid #1e1e2e;border-radius:12px;padding:20px 24px;color:#c0c0d0;font-size:14px;line-height:1.7;">
{brief}
</div>""", unsafe_allow_html=True)
    if st.button("Regenerer le Brief", use_container_width=True):
        st.session_state.pop("daily_brief", None)
        st.session_state.pop("last_brief_date", None)
        st.rerun()
