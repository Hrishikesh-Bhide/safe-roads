import streamlit as st
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Get the Google Maps API key from the environment
api_key = os.getenv("GOOGLE_MAPS_API_KEY")

# Define the coordinates (latitude and longitude)
latitude = 37.7749  # Example latitude
longitude = -122.4194  # Example longitude

# Create a Google Maps URL with the provided coordinates
google_maps_url = f"https://www.google.com/maps/embed/v1/place?key={api_key}&q={latitude},{longitude}"

# Display the Google Map in the Streamlit app
st.title("Google Map Viewer")

st.markdown(f"Latitude: {latitude}, Longitude: {longitude}")
st.markdown(f"Open the map below:")
st.markdown(f'<iframe width="100%" height="500" src="{google_maps_url}" frameborder="0" allowfullscreen></iframe>', unsafe_allow_html=True)