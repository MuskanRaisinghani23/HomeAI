import streamlit as st
from auth.login import login
from auth.signup import signup
from dashboard.home import home

def main():
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False

    if st.session_state["authenticated"]:
        st.sidebar.title("Navigation")
        page = st.sidebar.selectbox("Choose a page", ["Home", "Logout"])

        if page == "Home":
            home()
        elif page == "Logout":
            st.session_state["authenticated"] = False
            st.rerun()
    else:
        page = st.selectbox("Choose a page", ["Login", "Sign Up"], index=0, key="auth_page")

        if page == "Login":
            login()
        elif page == "Sign Up":
            signup()
if __name__ == "__main__":
    main()