import streamlit as st

def set_background():
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url("https://example.com/background.jpg");
            background-attachment: fixed;
            background-size: cover;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

