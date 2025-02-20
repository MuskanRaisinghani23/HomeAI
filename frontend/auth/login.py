import streamlit as st
from auth.users_db import users_db

def login():
    st.title("Login")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    st.markdown("""
       <style>
       .stButton button {
           width: 100%;
       }
        </style>
        """, unsafe_allow_html=True)
    if st.button("Login"):
        if email in users_db and users_db[email]["password"] == password:
            st.session_state["authenticated"] = True
            st.session_state["username"] = users_db[email]["username"]
            st.success("Logged in successfully!")
            st.rerun()
        else:
            st.error("Invalid email or password")