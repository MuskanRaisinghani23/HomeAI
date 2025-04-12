import streamlit as st
from auth.login import login
from auth.signup import signup
import pages.dashboard as dashboard
import pages.listing as listing
import pages.preference as preference

def main(): 
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False

    if st.session_state["authenticated"]:
        st.sidebar.title("Navigation")
        selection = st.sidebar.radio("Go to", ["Dashboard", "Listing", "Preference","Logout"])
        if selection == "Dashboard":
            dashboard.dashboard()
        elif selection == "Listing":
            listing.listing()
        elif selection == "Preference":
            preference.preference()
        elif selection == "Logout":
            st.session_state["authenticated"] = False
            st.rerun()
    else:
        tab1, tab2 = st.tabs(["Login", "Signup"])
        with tab1:
            login()
            
        with tab2:
            signup()
if __name__ == "__main__":
    main()