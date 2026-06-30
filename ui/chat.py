import streamlit as st
from agent.analyst import chat_with_agent


def render_chat(news, prices):
    st.subheader("💬 Chat avec l'Analyste IA")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    news_context = "\n".join([f"- {a['title']}" for a in news[:10]])
    prices_context = "\n".join([f"{k}: {v['price']} ({v['change_1d']:+.2f}%)" for k, v in prices.items()])

    if prompt := st.chat_input("Pose une question sur les marchés..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("L'analyste réfléchit..."):
                response = chat_with_agent(prompt, news_context, prices_context)
                st.markdown(response)
                st.session_state.messages.append({"role": "assistant", "content": response})

    if st.session_state.messages and st.button("🗑️ Effacer l'historique"):
        st.session_state.messages = []
        st.rerun()
