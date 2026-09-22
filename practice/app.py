import streamlit as st
from agent import generate_post

st.title("AI-ассистент для контент_мейкера")

topic = st.text_input("Тема поста")
platform = st.selectbox("Платформа", ["Instagram", "LinkedIn", "TikTok", "Telegram"])
tone = st.selectbox("Тон", ["дружелюбный", "экспертный", "провокационный", "нейтральный"])

if st.button("Сгенерировать"):
    if topic:
        result = generate_post(topic, platform, tone)
        st.subheader("Пост")
        st.write(result["post"])
        st.subheader("Варианты заголовков")
        for headline in result["headlines"]:
            st.write(f"- {headline}")
    else:
        st.warning("Сначала введи тему поста")