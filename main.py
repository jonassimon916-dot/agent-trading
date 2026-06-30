import os
from datetime import datetime, date
import streamlit as st

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

st.set_page_config(page_title="AI Trading Terminal", page_icon="", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;600&display=swap');
* { font-family: 'Inter', -apple-system, sans-serif; }
html, body, .stApp { background: #0a0a0f !important; color: #e1e1e6; }
.stApp header { background: #12121a !important; border-bottom: 1px solid #1e1e2e; }
[data-testid="stMetric"] {
  background: linear-gradient(135deg, #15152a 0%, #1a1a35 100%);
  border: 1px solid #2a2a4a; border-radius: 12px; padding: 16px;
  transition: all 0.3s ease;
}
[data-testid="stMetric"]:hover { border-color: #4a4a8a; transform: translateY(-2px); box-shadow: 0 4px 20px rgba(88,166,255,0.1); }
[data-testid="stMetric"] label { color: #7878a0 !important; font-size: 13px !important; font-weight: 500 !important; text-transform: uppercase; letter-spacing: 0.5px; }
[data-testid="stMetric"] [data-testid="stMetricValue"] { color: #f0f0ff !important; font-size: 26px !important; font-weight: 700 !important; }
[data-testid="stMetricDelta"] { font-size: 14px !important; font-weight: 600 !important; }
.stApp .stButton button {
  border-radius: 8px; font-weight: 500; font-size: 12px; padding: 4px 14px;
  transition: all 0.2s; border: 1px solid #2a2a4a; background: #15152a; color: #a0a0c0;
}
.stApp .stButton button:hover { border-color: #4a4a8a; background: #1a1a35; }
.stApp .stButton button[kind="primary"] { background: #1a6b3c; border: 1px solid #238636; color: #fff; }
.stApp .stButton button[kind="primary"]:hover { background: #238636; }
.stApp [data-testid="stExpander"] { background: #12121a; border: 1px solid #1e1e2e; border-radius: 12px; }
.stApp [data-testid="stExpander"] summary { color: #e1e1e6; font-weight: 500; }
.stApp hr { border-color: #1e1e2e; margin: 16px 0; }
.stApp .stChatMessage { background: #15152a; border: 1px solid #2a2a4a; border-radius: 12px; padding: 12px 16px; margin: 4px 0; }
.stApp .stChatInput { border: 1px solid #2a2a4a !important; border-radius: 12px !important; background: #15152a !important; }
.stApp .stChatInput input { color: #e1e1e6 !important; }
.stApp .stSpinner > div { border-color: #7878ff #7878ff transparent transparent !important; }
.stApp h1, .stApp h2, .stApp h3, .stApp h4 { color: #f0f0ff !important; }
.stApp .stCaption, .stApp .stMarkdown p { color: #7878a0; }
.stApp .stTabs [data-baseweb="tab-list"] { gap: 4px; border-bottom: 1px solid #1e1e2e; }
.stApp .stTabs [data-baseweb="tab"] {
  background: transparent; color: #7878a0; border-radius: 8px 8px 0 0;
  padding: 8px 20px; font-size: 13px; font-weight: 500; border: none; border-bottom: 2px solid transparent;
}
.stApp .stTabs [aria-selected="true"] { color: #f0f0ff !important; border-bottom: 2px solid #7878ff !important; background: transparent !important; }
.stApp [data-testid="stHorizontalBlock"] { gap: 8px; }
.stApp .stTextInput input { background: #15152a; border: 1px solid #2a2a4a; color: #e1e1e6; border-radius: 8px; }
.stApp .stMultiSelect [data-baseweb="select"] { background: #15152a; border: 1px solid #2a2a4a; border-radius: 8px; }
.stApp .st-bb { border-color: #2a2a4a; }
::-webkit-scrollbar { width: 6px; background: #0a0a0f; }
::-webkit-scrollbar-thumb { background: #2a2a4a; border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: #3a3a5a; }
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
now_h, now_m = datetime.now().hour, datetime.now().minute
if st.session_state.last_brief_date != str(today) and now_h >= DAILY_BRIEF_HOUR and now_m >= DAILY_BRIEF_MINUTE:
    with st.spinner("Generation du brief quotidien..."):
        st.session_state.daily_brief = generate_daily_brief(
            st.session_state.news, st.session_state.prices, st.session_state.calendar_events)
        st.session_state.last_brief_date = str(today)

now_str = datetime.now().strftime("%d/%m/%Y %H:%M")
st.markdown(f"""<div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:8px;">
<div style="display:flex;align-items:center;gap:12px;">
<span style="font-size:24px;font-weight:700;background:linear-gradient(135deg,#7878ff,#58a6ff);-webkit-background-clip:text;-webkit-text-fill-color:transparent;">AI Trading Terminal</span>
<span style="color:#3a3a5a;font-size:18px;font-weight:300;">|</span>
<span style="color:#7878a0;font-size:13px;">Macro & Market Intelligence</span>
</div>
<div style="display:flex;align-items:center;gap:16px;">
<span style="color:#3a3a5a;font-size:12px;font-family:monospace;">{now_str}</span>
<span style="background:#1a6b3c20;border:1px solid #1a6b3c;border-radius:6px;padding:2px 10px;color:#3fb950;font-size:11px;">LIVE</span>
</div></div>""", unsafe_allow_html=True)

render_prices(st.session_state.prices)

render_calendar(st.session_state.calendar_events)

t1, t2 = st.tabs(["Brief & Actualites", "Graphiques"])
with t1:
    cb, cn = st.columns([3, 2])
    with cb:
        render_daily_brief(st.session_state.daily_brief)
    with cn:
        st.markdown(f"""<div style="background:linear-gradient(135deg,#15152a,#1a1a35);border:1px solid #2a2a4a;border-radius:12px;padding:12px 16px;margin-bottom:12px;">
<span style="color:#f0f0ff;font-weight:600;font-size:14px;">Flash News</span>
<span style="color:#3a3a5a;font-size:11px;margin-left:8px;">{len(st.session_state.news)} updates</span></div>""", unsafe_allow_html=True)
        for a in st.session_state.news[:6]:
            with st.container(border=True):
                st.markdown(f"**{a['title']}**")
                st.caption(f"{a.get('source','')} | {str(a.get('published',''))[:16]}")
                if st.button("AI", key=f"n_{a.get('id','x')[:8]}", use_container_width=True):
                    from agent.analyst import analyze_sentiment
                    with st.spinner("Analyse..."):
                        r = analyze_sentiment(a)
                    s = r.get("sentiment","neutral")
                    st.info(f"{'🟢' if s=='bullish' else '🔴' if s=='bearish' else '⚪'} Sentiment: **{s}**")
                    st.json(r)
        if st.button("Refresh", use_container_width=True):
            st.session_state.news = get_all_news()
            st.rerun()
with t2:
    render_charts()

st.markdown("---")
render_chat(st.session_state.news, st.session_state.prices, st.session_state.calendar_events)

from config import LLM_PROVIDER
st.markdown(f"""<div style="text-align:center;padding:8px 0;border-top:1px solid #1e1e2e;margin-top:12px;">
<span style="color:#3a3a5a;font-size:11px;">AI Trading Terminal  |  Yahoo Finance + TradingView + Groq  |  LLM: {LLM_PROVIDER}</span>
</div>""", unsafe_allow_html=True)
