import streamlit as st
from components.login import login
from components.signup import signup
import components.dashboard as dashboard
import components.listing as listing
import components.preference as preference

PAGES = {
    "Preference": preference,
    "Listing": listing,
    "Dashboard": dashboard
}

def main(): 
    st.set_page_config(page_title="HomeAI")
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False

    if not st.session_state["authenticated"]:
        st.markdown(
            """
            <style>
                [data-testid="stSidebar"] {
                    display: none;
                }
            </style>
            """,
            unsafe_allow_html=True,
        )
        st.title("HomeAI")
        st.title("Login/Signup")
        tab1, tab2 = st.tabs(["Login", "Signup"])
        with tab1:
            login()
            
        with tab2:
            signup()
    else:
        st.sidebar.title("Menu")
        selection = st.sidebar.radio("Go to", list(PAGES.keys()))
        if st.sidebar.button('Logout'):
            st.session_state['authenticated'] = False
            # del st.session_state['access_token']
            st.rerun()

        if st.session_state['authenticated']:
            page = PAGES[selection]
            page_function = getattr(
                page, selection.lower())
            page_function()

if __name__ == "__main__":
    main()