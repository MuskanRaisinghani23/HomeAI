import streamlit as st
import requests

STATE_CITY_MAP = {
    "MA": ["Boston", "Cambridge", "Somerville"],
    "CA": ["San Francisco", "Los Angeles", "San Diego"],
    "NY": ["New York", "Buffalo", "Rochester"]
}

def preference():
    st.title("Add your preference here for personalized recommendations")

    st.subheader("Update preference Information")

    selected_state = st.selectbox("Select State", options=list(STATE_CITY_MAP.keys()))
    selected_location = st.selectbox("Select Location", options=STATE_CITY_MAP[selected_state])

    with st.form(key='preference_form'):
        budget = st.slider("Budget Range", min_value=100, max_value=5000, value=(200, 3000), step=50)
        room_type = st.selectbox("Room Type", options=["Private", "Shared"])
        laundry_available = st.radio("Laundry Available", options=["Yes", "No"])

        submit_button = st.form_submit_button(label='Save')

    if submit_button:
        payload = {
            "location": selected_location,
            "min_price": budget[0],
            "max_price": budget[1],
            "room_type": room_type,
            "laundry_availability": True if laundry_available == "Yes" else False
        }

        try:
            response = requests.get("http://127.0.0.1:8000/api/listing/get-listings", params=payload)
            response.raise_for_status()
            st.session_state.filtered_listings = response.json().get("data", [])
            st.success("Preference saved and listings updated!")
        except Exception as e:
            st.error(f"Error fetching listings: {str(e)}")