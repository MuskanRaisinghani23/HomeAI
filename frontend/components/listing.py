import streamlit as st
import requests
import re
import unicodedata

def clean_description(text):
    # Normalize Unicode to ASCII to remove fancy characters
    text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode()

    text = re.sub(r"(?:\n)?(?:[\*•]+ ?)(?=\w)", r"\n• ", text)
    text = re.sub(r"(•\s*){2,}", "• ", text)
    text = re.sub(r"[`_=]", "", text)
    text = re.sub(r"^\s*•\s*", "", text)
    text = re.sub(r"\n\s*•\s*\n", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()

@st.dialog("Listing Details")
def more_details(listing):
    st.write(f"**Laundry Available:** {listing['laundry_available']}")
    st.write(f"**Room Type:** {listing['room_type']}")
    st.write(f"**Bathroom Count:** {listing['bath_count']}")
    st.link_button("Open Listing", listing["listing_url"])

def listing():
    st.title("Available Listings")

    listings = st.session_state.get("filtered_listings", [])

    if listings:
        for listing in listings:
            st.markdown(
                f"""
                <div style=\"border: 1px solid #e0e0e0; border-radius: 10px; padding: 20px; margin: 10px 0; box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);\">
                    <h3 style=\"margin: 0;\">Price: {listing['price']}</h3>
                    <p style=\"margin: 5px 0;\">Location: {listing['location']}</p>
                    <p style="margin: 5px 0; white-space: pre-wrap;">Summary: {clean_description(listing['description'])}</p>
                    <p style=\"margin: 5px 0;\">Listing Date: {listing['listing_date']}</p>
                    <p style=\"margin: 5px 0;\">Source: {listing['source']}</p>
                </div>
                """,
                unsafe_allow_html=True
            )
            if st.button("More Details", key=listing["listing_url"]):
                more_details(listing=listing)
    else:
        st.info("No listings available at the moment.")

    # with col2:
    #     st.subheader("HomeAI Chat Bot")

    #     if "messages" not in st.session_state:
    #         st.session_state.messages = []

    #     chat_container = st.empty()

    #     def render_chat():
    #         with chat_container.container():
    #             st.markdown(
    #                 """
    #                 <style>
    #                 div[data-testid=\"stVerticalBlock\"] > div:first-child {
    #                     max-height: 840px !important;
    #                     overflow-y: auto !important;
    #                 }
    #                 </style>
    #                 """, unsafe_allow_html=True
    #             )
    #             for message in st.session_state.messages:
    #                 with st.chat_message(message["role"]):
    #                     st.write(message["content"])

    #     render_chat()

    #     user_input = st.chat_input("Ask me anything", key="chat_input")

    #     if user_input:
    #         st.session_state.messages.append({"role": "user", "content": user_input})
    #         bot_response = f"You said: {user_input}"
    #         st.session_state.messages.append({"role": "assistant", "content": bot_response})
    #         st.rerun()