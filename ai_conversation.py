import openai
import streamlit as st

# Set up your OpenAI API key
openai.api_key = st.secrets["openai_api_key"]

def chat_with_ai(user_input):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful language learning assistant."},
            {"role": "user", "content": user_input}
        ]
    )
    return response.choices[0].message['content']

