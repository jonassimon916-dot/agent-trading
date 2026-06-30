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
from agent.calendar_collector import fetch_calendar
from ui.dashboard import render_prices, render_charts, render_daily_brief
from ui.calendar_view import render_calendar
from ui.chat import render_chat

st.set_page_config(
    page_title="AI Trading Terminal",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
.stApp { background: #0d1117; }
.stApp header { background: #161b22 !important; }
.stApp .stTabs [data-baseweb="tab-list"] { gap: 2px; }
.stApp .stTabs [data-baseweb="tab"] { background: #161b22; border-radius: 6px 6px 0 0; padding: 8px 16px; }
.stApp [data-testid="stMetric"] { background: #161b22; border: 1px solid #30363d; border-radius: 8px; padding: 12px; }
.stApp [data-testid="stMetric"] label { color: #8b949e !important; }
.stApp [data-testid="stMetric"] [data-testid="stMetricValue"] { color: #e6edf3 !important; }
.stApp [data-testid="stMetricDelta"] { font-size: 14px !important; }
.stApp .st-emotion-cache-1r4qj8v { background: #161b22; border: 1px solid #30363d; border-radius: 8px; }
.stApp .stButton button { border-radius: 6px; font-weight: 500; font-size: 13px; }
.stApp .stButton button[kind="primary"] { background: #238636; border: 1px solid #2ea043; }
.stApp .stTextInput input { background: #161b22; border: 1px solid #30363d; color: #e6edf3; }
.stApp hr { border-color: #30363d; }
.stApp .stChatMessage { background: #161b22; border: 1px solid #30363d; border-radius: 8px; padding: 8px 12px; }
.stApp .stChatInput { background: #161b22; border: 1px solid #30363d; border-radius: 8px; }
.stApp .stSpinner > div { border-color: #58a6ff; }
.stApp h1, .stApp h2, .stApp h3 { color: #e6edf3 !important; }
.stApp .stCaption { color: #8b949e; }
.stApp .stExpander { background: #161b22; border: 1px solid #30363d; border-radius: 8px; }
.stApp .stExpander summary { color: #e6edf3; }
</style>
""", unsafe_allow_html=True)

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
        with st.spinner("Generation du brief quotidien..."):
            st.session_state.daily_brief = generate_daily_brief(
                st.session_state.news,
                st.session_state.prices,
                st.session_state.calendar_events,
            )
            st.session_state.last_brief_date = str(today)

st.markdown(f'<div style="display:flex;align-items:center;gap:12px;margin-bottom:4px;">'
            f'<span style="font-size:28px;">📊</span>'
            f'<div><span style="font-size:24px;font-weight:700;color:#e6edf3;">AI Trading Terminal</span>'
            f'<br><span style="font-size:13px;color:#8b949e;">Derniere mise a jour: {datetime.now().strftime("%d/%m/%Y %H:%M")} | Auto-refresh: {POLL_INTERVAL_MINUTES}min</span></div>'
            f'</div>', unsafe_allow_html=True)

render_prices(st.session_state.prices)

render_calendar(st.session_state.calendar_events)

brief_tab, charts_tab = st.tabs(["Brief Macro", "Graphiques 30 jours"])
with brief_tab:
    col_b, col_n = st.columns([3, 2])
    with col_b:
        render_daily_brief(st.session_state.daily_brief)
    with col_n:
        st.markdown('<div style="background:#161b22;border:1px solid #30363d;border-radius:8px;padding:12px;margin-bottom:12px;">'
                    '<span style="color:#e6edf3;font-weight:600;font-size:15px;">Actualites</span></div>',
                    unsafe_allow_html=True)
        for a in st.session_state.news[:7]:
            with st.container(border=True):
                st.markdown(f"**{a['title']}**")
                st.caption(f"{a['source']}  |  {str(a.get('published',''))[:16]}")
                if st.button("Analyser", key=f"n_{a['id'][:8]}", use_container_width=True):
                    from agent.analyst import analyze_sentiment
                    with st.spinner("Analyse en cours..."):
                        analysis = analyze_sentiment(a)
                    s = analysis.get("sentiment", "N/A")
                    icon = "🟢" if s == "bullish" else ("🔴" if s == "bearish" else "⚪")
                    st.info(f"{icon} Sentiment: **{s}**")
                    st.json(analysis)
        if st.button("Rafraichir", use_container_width=True):
            st.session_state.news = get_all_news()
            st.rerun()

with charts_tab:
    render_charts()

st.markdown("---")
render_chat(st.session_state.news, st.session_state.prices, st.session_state.calendar_events)

st.markdown("---")
from config import LLM_PROVIDER
st.markdown(f'<div style="text-align:center;color:#8b949e;font-size:12px;">'
            f'AI Trading Terminal v1.0 | Yahoo Finance + TradingView + Groq | LLM: {LLM_PROVIDER}</div>',
            unsafe_allow_html=True)
