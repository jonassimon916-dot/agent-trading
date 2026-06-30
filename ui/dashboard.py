import streamlit as st
import plotly.graph_objects as go
from datetime import datetime
from agent.market_data import fetch_current_prices, fetch_historical_data


def render_prices(prices):
    st.subheader("Prix en Direct")
    cols = st.columns(len(prices))
    for i, (key, data) in enumerate(prices.items()):
        with cols[i]:
            color = "green" if data["change_1d"] >= 0 else "red"
            arrow = "▲" if data["change_1d"] >= 0 else "▼"
            st.metric(
                label=f"{data['name']} ({key})",
                value=f"${data['price']:,.2f}",
                delta=f"{arrow} {data['change_1d']:+.2f}% (24h)",
                delta_color="normal",
            )


def render_charts():
    st.subheader("Évolution des Prix")
    hist_data = fetch_historical_data("1mo")
    if not hist_data:
        st.info("Données historiques non disponibles")
        return
    tabs = st.tabs(list(hist_data.keys()))
    for i, (key, df) in enumerate(hist_data.items()):
        with tabs[i]:
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=df["Date"], y=df["Close"],
                mode="lines",
                name=key,
                line=dict(color="royalblue", width=2),
            ))
            fig.update_layout(
                title=f"{key} - 30 jours",
                xaxis_title="Date",
                yaxis_title="Prix ($)",
                height=400,
                margin=dict(l=20, r=20, t=40, b=20),
            )
            st.plotly_chart(fig, use_container_width=True)


def render_daily_brief(brief):
    if not brief:
        st.warning("Génération du brief en cours... Actualise la page dans quelques instants.")
        return
    st.subheader("Brief Macro-Économique Quotidien")
    st.markdown(f"**Dernière mise à jour:** {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    st.markdown("---")
    st.markdown(brief)
    st.markdown("---")
    if st.button("🔄 Régénérer le Brief"):
        st.session_state.pop("daily_brief", None)
        st.session_state.pop("last_brief_date", None)
        st.rerun()
