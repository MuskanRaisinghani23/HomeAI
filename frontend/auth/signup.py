import streamlit as st
from auth.users_db import users_db

def signup():
    st.title("Sign Up")
    username = st.text_input("Username")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    confirm_password = st.text_input("Confirm Password", type="password")
    
    # Address fields
    address_line1 = st.text_input("Address Line 1")
    address_line2 = st.text_input("Address Line 2")
    city = st.text_input("City")
    col1, col2 = st.columns(2)        
    with col1:
        state = st.text_input("State")
    with col2:
        zipcode = st.text_input("Zipcode")

    selected_tags = st.multiselect("Select Tags", ["Sports", "Politics", "Technology", "Health"])
 
    st.markdown("""
       <style>
       .stButton button {
           width: 100%;
       }
        </style>
        """, unsafe_allow_html=True)
    if st.button("Sign Up"):
        if not username or not email or not password or not confirm_password or not address_line1 or not city or not state or not zipcode:
            st.error("Please fill out all required fields.")
        elif password != confirm_password:
            st.error("Passwords do not match")
        elif email in users_db:
            st.error("Email already exists")
        else:
            users_db[email] = {
                "username": username,
                "password": password,
                "address": {
                    "line1": address_line1,
                    "line2": address_line2,
                    "city": city,
                    "state": state,
                    "zipcode": zipcode
                },
                "tags": selected_tags
            }
            st.success("Account created successfully! Please log in.")
            st.rerun()

# Example users_db structure
users_db = {
    "test@example.com": {
        "username": "testuser",
        "password": "password123",
        "address": {
            "line1": "123 Main St",
            "line2": "",
            "city": "Anytown",
            "state": "CA",
            "zipcode": "12345"
        },
        "tags": ["Technology"]
    }
}