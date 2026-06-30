import streamlit as st
from agent.analyst import chat_with_agent
from agent.calendar_collector import format_calendar_for_prompt


def render_chat(news, prices, calendar_events=None):
    st.markdown(f"""<div style="background:linear-gradient(135deg,#15152a,#1a1a35);border:1px solid #2a2a4a;border-radius:12px;padding:12px 16px;margin-bottom:12px;display:flex;justify-content:space-between;align-items:center;">
<div><span style="color:#f0f0ff;font-weight:600;font-size:14px;">Assistant IA</span>
<span style="color:#3a3a5a;font-size:11px;margin-left:8px;">Pose une question sur les marches</span></div>
</div>""", unsafe_allow_html=True)

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    news_ctx = "\n".join([f"- {a['title']}" for a in news[:8]])
    prices_ctx = "\n".join([f"{k}: {v['price']} ({v['change_1d']:+.2f}%)" for k, v in prices.items()])
    cal_ctx = format_calendar_for_prompt(calendar_events or [], 8)

    if prompt := st.chat_input("Ex: Que penses-tu de l'or cette semaine ?"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        with st.chat_message("assistant"):
            with st.spinner(""):
                response = chat_with_agent(prompt, news_ctx, prices_ctx, cal_ctx)
                st.markdown(response)
                st.session_state.messages.append({"role": "assistant", "content": response})

    if st.session_state.messages and st.button("Effacer l'historique", use_container_width=True):
        st.session_state.messages = []
        st.rerun()
