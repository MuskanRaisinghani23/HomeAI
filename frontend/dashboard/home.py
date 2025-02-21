import streamlit as st

def home():
    st.title("Welcome to HomeAI")
    st.markdown("<h1 style='text-align: center; color: blue;'>Welcome to <i>HomeAI</i></h1>", unsafe_allow_html=True)
    st.write("This is a basic Streamlit application with a collapsible sidebar.")
    number = st.slider("Pick a number", 0, 100, 10)
    st.write(f"You selected {number}")
    if st.button("Click me"):
        st.write("Button clicked!")