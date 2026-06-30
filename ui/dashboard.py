import streamlit as st
import plotly.graph_objects as go
from datetime import datetime, timedelta
from agent.market_data import fetch_current_prices, fetch_historical_data
from agent.calendar_collector import get_calendar_for_dashboard, CURRENCY_DATA

IMPACT_COLORS = {1: "#ef5350", 0: "#ff9800", -1: "#9e9e9e"}
IMPACT_DOT = {1: "🔴", 0: "🟠", -1: "⚪"}


def render_prices(prices):
    st.subheader("Prix en Direct")
    cols = st.columns(len(prices))
    for i, (key, data) in enumerate(prices.items()):
        with cols[i]:
            arrow = "▲" if data["change_1d"] >= 0 else "▼"
            st.metric(
                label=f"{data['name']} ({key})",
                value=f"${data['price']:,.2f}",
                delta=f"{arrow} {data['change_1d']:+.2f}% (24h)",
                delta_color="normal",
            )


def render_charts():
    st.subheader("Evolution des Prix")
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
                line=dict(color="royalblue", width=2),
            ))
            fig.update_layout(
                title=f"{key} - 30 jours",
                xaxis_title="Date", yaxis_title="Prix ($)",
                height=400, margin=dict(l=20, r=20, t=40, b=20),
            )
            st.plotly_chart(fig, use_container_width=True)


def render_daily_brief(brief):
    if not brief:
        st.warning("Generation du brief en cours... Actualise dans quelques instants.")
        return
    st.subheader("Brief Macro-Economique Quotidien")
    st.markdown(f"**Derniere mise a jour:** {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    st.markdown("---")
    st.markdown(brief)
    st.markdown("---")
    if st.button("Regenerer le Brief"):
        st.session_state.pop("daily_brief", None)
        st.session_state.pop("last_brief_date", None)
        st.rerun()


def render_calendar(events):
    st.subheader("Calendrier Economique")

    if not events:
        st.caption("Aucun evenement trouve")
        return

    today = datetime.now().strftime("%Y-%m-%d")
    tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
    prev_day = None
    count = 0
    max_show = 20

    for e in events:
        if count >= max_show:
            break

        day = e.get("day", "")
        time_str = e.get("time", "") or "--:--"

        if day and day != prev_day:
            if prev_day is not None:
                st.markdown("---")
            if day == today:
                label = f"Aujourd'hui {day}"
            elif day == tomorrow:
                label = f"Demain {day}"
            else:
                try:
                    d = datetime.strptime(day, "%Y-%m-%d")
                    label = d.strftime("%A %d %B").capitalize()
                except:
                    label = day
            st.markdown(f"**{label}**")
            prev_day = day

        imp = e.get("impact", -1)
        dot = IMPACT_DOT.get(imp, "⚪")
        currency = e.get("currency", "")
        flag = CURRENCY_DATA.get(currency, {}).get("flag", "")

        actual = e.get("actual", "") or "-"
        forecast = e.get("forecast", "") or "-"
        previous = e.get("previous", "") or "-"

        act_color = ""
        if e.get("direction") == "up":
            act_color = "#4caf50"
        elif e.get("direction") == "down":
            act_color = "#ef5350"

        html = f"""<div style="display:flex; align-items:center; padding:3px 0; font-size:14px; gap:8px;">
  <span style="font-size:16px;">{dot}</span>
  <span style="color:#888; width:45px;">{time_str}</span>
  <span style="width:30px;">{flag}</span>
  <span style="flex:1; font-weight:{'600' if imp >= 0 else '400'};">{e.get('event', '')[:40]}</span>
  <span style="width:70px; text-align:right; color:{act_color}; font-weight:600;">{actual}</span>
  <span style="width:70px; text-align:right; color:#888;">{forecast}</span>
  <span style="width:70px; text-align:right; color:#666;">{previous}</span>
</div>"""
        st.markdown(html, unsafe_allow_html=True)
        count += 1

    if len(events) > max_show:
        st.caption(f"+ {len(events) - max_show} evenements supplementaires")
    else:
        st.caption(f"{len(events)} evenements a venir (7 jours)")
