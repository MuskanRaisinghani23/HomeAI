import streamlit as st
import requests

def preference():
    st.title("Add your preference here for personalized recommendations")

    st.subheader("Update preference Information")

    with st.form(key='preference_form'):
        budget = st.number_input("Budget", min_value=0, step=1)
        room_type = st.selectbox("Room Type", options=["Private", "Shared"])
        location = st.text_input("Location")
        people_count = st.number_input("People Count", min_value=0, max_value=99, step=1)

        submit_button = st.form_submit_button(label='Save')

    if submit_button:
        # Call the API to update the preference in Snowflake
        payload = {
            "budget": budget,
            "room_type": room_type,
            "location": location,
            "people_count": people_count
        }
        # Make a POST request to the backend API
        response = requests.post("http://localhost:8001/api/preference//update-preference", json=payload) # Update based on the backend port
        # Check the response from the API
        if response.status_code == 200:
            response_data = response.json()
            if response_data["status"] == "success":
                st.success("Preference updated successfully!")
            else:
                st.error(f"Error: {response_data['message']}")
        else:
            st.error("Failed to update preference. Please try again later.")
        