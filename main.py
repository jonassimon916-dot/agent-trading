import streamlit as st
import os
from datetime import datetime, date

for key in ["LLM_PROVIDER", "GROQ_API_KEY", "NEWSAPI_KEY", "FRED_API_KEY"]:
    if key in st.secrets:
        os.environ[key] = str(st.secrets[key])

from streamlit_autorefresh import st_autorefresh
from config import POLL_INTERVAL_MINUTES, DAILY_BRIEF_HOUR, DAILY_BRIEF_MINUTE
from agent.news_collector import get_all_news
from agent.market_data import fetch_current_prices
from agent.analyst import generate_daily_brief
from agent.calendar_collector import fetch_calendar, format_calendar_for_prompt
from ui.dashboard import render_prices, render_charts, render_daily_brief
from ui.calendar_view import render_calendar
from ui.chat import render_chat

st.set_page_config(
    page_title="Agent IA Trading",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st_autorefresh(interval=POLL_INTERVAL_MINUTES * 60 * 1000, key="auto_refresh")

if "prices" not in st.session_state:
    st.session_state.prices = fetch_current_prices()
if "news" not in st.session_state:
    st.session_state.news = get_all_news()
if "daily_brief" not in st.session_state:
    st.session_state.daily_brief = ""
if "last_brief_date" not in st.session_state:
    st.session_state.last_brief_date = None
if "calendar_events" not in st.session_state:
    st.session_state.calendar_events = fetch_calendar(7)

today = date.today()
brief_hour = datetime.now().hour
brief_min = datetime.now().minute

if st.session_state.last_brief_date != str(today):
    if brief_hour >= DAILY_BRIEF_HOUR and brief_min >= DAILY_BRIEF_MINUTE:
        with st.spinner("Génération du brief quotidien..."):
            st.session_state.daily_brief = generate_daily_brief(
                st.session_state.news,
                st.session_state.prices,
                st.session_state.calendar_events,
            )
            st.session_state.last_brief_date = str(today)

st.title("📈 Agent IA Trading & Macro-Économie")
st.caption(f"Dernière mise à jour: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')} | Intervalle: {POLL_INTERVAL_MINUTES} min")

render_prices(st.session_state.prices)

with st.expander("📊 Graphiques 30 jours", expanded=False):
    render_charts()

col1, col2 = st.columns([2, 1])

with col1:
    render_daily_brief(st.session_state.daily_brief)

with col2:
    render_calendar(st.session_state.calendar_events)

    st.subheader("📰 Dernières Actualités")
    for a in st.session_state.news[:10]:
        with st.container(border=True):
            st.markdown(f"**{a['title']}**")
            st.caption(f"📌 {a['source']} • {a.get('published', '')[:16]}")
            if st.button("🔍 Analyser", key=f"news_{a['id'][:8]}"):
                from agent.analyst import analyze_sentiment
                with st.spinner("Analyse en cours..."):
                    analysis = analyze_sentiment(a)
                st.info(f"**Sentiment:** {analysis.get('sentiment', 'N/A')}")
                st.json(analysis)

    if st.button("🔄 Rafraîchir les News"):
        st.session_state.news = get_all_news()
        st.rerun()

st.markdown("---")
render_chat(st.session_state.news, st.session_state.prices, st.session_state.calendar_events)

st.markdown("---")
from config import LLM_PROVIDER
st.caption(f"Agent IA Trading v1.0 | Données via Yahoo Finance, NewsAPI, RSS | LLM: {LLM_PROVIDER}")
