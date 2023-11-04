import streamlit as st
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

with st.sidebar:

    source_location = st.text_input("Enter Source")
    destination_location = st.text_input("Enter Destination")

    find_safe_route = st.button("Submit")

if find_safe_route == True:
   st.title("Google Map in Streamlit")

   # Replace 'your_api_key' with your actual Google Maps API key
   api_key = os.getenv("GOOGLE_MAPS_API_KEY")

   # Define the location and zoom lev
   latitude = 40.7128
   longitude = -74.0060
   zoom_level = 12

   # Create the Google Maps URL
   google_maps_url = f"https://www.google.com/maps/embed/v1/view?key={api_key}&center={latitude},{longitude}&zoom={zoom_level}"

   # Use an iframe to embed the Google Map
   st.markdown(f'<iframe src="{google_maps_url}" width="100%" height="500" frameborder="0" style="border:0"></iframe>', unsafe_allow_html=True)