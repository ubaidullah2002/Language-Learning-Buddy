import streamlit as st
import sqlite3
import hashlib
from datetime import datetime
import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set up GroqCloud API key
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

# Database setup
def init_db():
    conn = sqlite3.connect('language_learning.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY, username TEXT UNIQUE, password TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS lessons
                 (id INTEGER PRIMARY KEY, title TEXT, content TEXT, language TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS user_progress
                 (user_id INTEGER, lesson_id INTEGER, completed_at TIMESTAMP,
                 FOREIGN KEY(user_id) REFERENCES users(id),
                 FOREIGN KEY(lesson_id) REFERENCES lessons(id))''')
    conn.commit()
    conn.close()

# User authentication
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def authenticate(username, password):
    conn = sqlite3.connect('language_learning.db')
    c = conn.cursor()
    c.execute("SELECT id, password FROM users WHERE username=?", (username,))
    user = c.fetchone()
    conn.close()
    if user and user[1] == hash_password(password):
        return user[0]
    return None

def create_user(username, password):
    conn = sqlite3.connect('language_learning.db')
    c = conn.cursor()
    try:
        c.execute("INSERT INTO users (username, password) VALUES (?, ?)",
                  (username, hash_password(password)))
        conn.commit()
        user_id = c.lastrowid
        conn.close()
        return user_id
    except sqlite3.IntegrityError:
        conn.close()
        return None

# Lesson management
def get_lessons(language):
    conn = sqlite3.connect('language_learning.db')
    c = conn.cursor()
    c.execute("SELECT id, title, content FROM lessons WHERE language=?", (language,))
    lessons = c.fetchall()
    conn.close()
    return lessons

def complete_lesson(user_id, lesson_id):
    conn = sqlite3.connect('language_learning.db')
    c = conn.cursor()
    c.execute("INSERT INTO user_progress (user_id, lesson_id, completed_at) VALUES (?, ?, ?)",
              (user_id, lesson_id, datetime.now()))
    conn.commit()
    conn.close()

def get_user_progress(user_id):
    conn = sqlite3.connect('language_learning.db')
    c = conn.cursor()
    c.execute("""SELECT lessons.title, user_progress.completed_at 
                 FROM user_progress 
                 JOIN lessons ON user_progress.lesson_id = lessons.id 
                 WHERE user_progress.user_id = ?""", (user_id,))
    progress = c.fetchall()
    conn.close()
    return progress

# AI conversation using GroqCloud
def chat_with_ai(user_input, language):
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "mixtral-8x7b-32768",
        "messages": [
            {"role": "system", "content": f"You are a helpful language learning assistant for {language}."},
            {"role": "user", "content": user_input}
        ]
    }
    response = requests.post(GROQ_API_URL, headers=headers, json=data)
    if response.status_code == 200:
        return response.json()['choices'][0]['message']['content']
    else:
        return "Sorry, I couldn't process your request at the moment."

# Streamlit app
def main():
    st.set_page_config(page_title="Language Learning Buddy", page_icon="🌍", layout="wide")
    
    # Custom CSS for improved UI
    st.markdown("""
    <style>
    .stApp {
        background-color: #f0f4f8;
        color: #1e3a5f;
    }
    .stButton>button {
        background-color: #4CAF50;
        color: white;
        font-weight: bold;
    }
    .stTextInput>div>div>input {
        background-color: #ffffff;
    }
    .stExpander {
        background-color: #ffffff;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    </style>
    """, unsafe_allow_html=True)

    st.title("🌍 Language Learning Buddy")

    # Initialize database
    init_db()

    # Session state
    if 'user_id' not in st.session_state:
        st.session_state.user_id = None
    if 'language' not in st.session_state:
        st.session_state.language = "English"

    # Sidebar for navigation and authentication
    with st.sidebar:
        st.image("https://example.com/logo.png", width=200)  # Replace with your logo
        menu = ["Home", "Lessons", "Practice", "Progress"]
        choice = st.selectbox("Menu", menu)

        if st.session_state.user_id is None:
            st.subheader("Login / Signup")
            auth_choice = st.radio("", ["Login", "Signup"])
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            
            if auth_choice == "Login":
                if st.button("Login", key="login"):
                    user_id = authenticate(username, password)
                    if user_id:
                        st.session_state.user_id = user_id
                        st.success("Logged in successfully!")
                        st.experimental_rerun()
                    else:
                        st.error("Invalid username or password")
            else:
                if st.button("Signup", key="signup"):
                    user_id = create_user(username, password)
                    if user_id:
                        st.session_state.user_id = user_id
                        st.success("Account created successfully!")
                        st.experimental_rerun()
                    else:
                        st.error("Username already exists")
        else:
            st.subheader(f"Welcome, User {st.session_state.user_id}!")
            if st.button("Logout"):
                st.session_state.user_id = None
                st.experimental_rerun()

        st.session_state.language = st.selectbox("Choose Language", ["English", "Spanish", "French", "German"])

    # Main content
    if choice == "Home":
        st.header("Welcome to Language Learning Buddy!")
        st.write("Choose a section from the menu to start learning.")
        st.image("https://example.com/language_learning.jpg", use_column_width=True)

    elif choice == "Lessons":
        if st.session_state.user_id:
            st.header(f"{st.session_state.language} Lessons")
            lessons = get_lessons(st.session_state.language)
            for lesson in lessons:
                with st.expander(f"Lesson: {lesson[1]}"):
                    st.write(lesson[2])
                    if st.button(f"Complete '{lesson[1]}'", key=f"complete_{lesson[0]}"):
                        complete_lesson(st.session_state.user_id, lesson[0])
                        st.success(f"Lesson '{lesson[1]}' completed!")
                        st.balloons()
        else:
            st.warning("Please login to access lessons.")

    elif choice == "Practice":
        if st.session_state.user_id:
            st.header("Conversational Practice")
            st.write(f"Practice your {st.session_state.language} skills with our AI assistant!")
            user_input = st.text_input("Type your message here:")
            if user_input:
                with st.spinner("AI is thinking..."):
                    response = chat_with_ai(user_input, st.session_state.language)
                st.write("AI: ", response)
        else:
            st.warning("Please login to access practice.")

    elif choice == "Progress":
        if st.session_state.user_id:
            st.header("Your Progress")
            progress = get_user_progress(st.session_state.user_id)
            if progress:
                for lesson, completed_at in progress:
                    st.success(f"Completed '{lesson}' on {completed_at}")
                
                # Create a bar chart of completed lessons
                lesson_counts = {}
                for lesson, _ in progress:
                    lesson_counts[lesson] = lesson_counts.get(lesson, 0) + 1
                
                st.subheader("Lessons Completed")
                st.bar_chart(lesson_counts)
            else:
                st.info("No progress data available yet. Start learning!")
        else:
            st.warning("Please login to view your progress.")

if __name__ == "__main__":
    main()

