import streamlit as st
import requests

@st.dialog("Listing Details")
def more_details(listing):
    st.write(f"**Price:** {listing['price']}")
    st.write(f"**Location:** {listing['location']}")
    st.write(f"**Summary:** {listing['description_summary']}")
    st.link_button("Open Listing", listing["listing_url"])

def listing():
    col1, col2 = st.columns(2, gap="large")

    with col1:
        st.title("Available Listings")
        # Fetch listings from the backend API
        try:
            headers = {
                "accept": "application/json",
                "Content-Type": "application/json"
            }

            response = requests.get("http://localhost:8001/api/listing/get-listings", headers=headers)
            response.raise_for_status()  # Raise an error for bad responses
            listings = response.json().get("data", [])
        except Exception as e:
            st.error(f"Error fetching listings: {str(e)}")
            listings = []

        # Display listings
        if listings:
            for listing in listings:
                # with st.container():
                #     st.write(f"**Price:** {l['price']}")
                #     st.write(f"**Location:** {l['location']}")
                #     st.write(f"**Summary:** {l['description_summary']}")

                #     # 4) Your Streamlit button lives in the same .card div
                #     if st.button("More Details", key=l["listing_url"]):
                #         more_details(l)

                st.markdown(
                    f"""
                    <div style="border: 1px solid #e0e0e0; border-radius: 10px; padding: 20px; margin: 10px 0; box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);">
                        <h3 style="margin: 0;">Price: {listing['price']}</h3>
                        <p style="margin: 5px 0;">Location: {listing['location']}</p>
                        <p style="margin: 5px 0;">Summary: {listing['description_summary']}</p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                if st.button("More Details", key=listing["listing_url"]):
                    more_details(listing=listing)
        else:
            st.info("No listings available at the moment.")
            return
    with col2:
        st.subheader("HomeAI Chat Bot")

        if "messages" not in st.session_state:
            st.session_state.messages = []

        chat_container = st.empty()  # Placeholder for chat messages

        # Function to render messages
        def render_chat():
            with chat_container.container():
                st.markdown(
                    """
                    <style>
                    div[data-testid="stVerticalBlock"] > div:first-child {
                        max-height: 840px !important;
                        overflow-y: auto !important;
                    }
                    </style>
                    """, unsafe_allow_html=True
                )
                for message in st.session_state.messages:
                    with st.chat_message(message["role"]):
                        st.write(message["content"])
        
        render_chat()  # Initial rendering

        # User input
        user_input = st.chat_input("Ask me anything", key="chat_input")

        if user_input:
            st.session_state.messages.append({"role": "user", "content": user_input})
            bot_response = f"You said: {user_input}"
            st.session_state.messages.append({"role": "assistant", "content": bot_response})

            # render_chat()  # Update chat UI

            # Force rerun to trigger scrolling
            st.rerun()
