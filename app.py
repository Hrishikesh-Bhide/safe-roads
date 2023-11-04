import streamlit as st
import requests
from dotenv import load_dotenv
import os
from geopy.geocoders import Nominatim
import polyline
import pandas as pd

# Load environment variables from .env file
load_dotenv()

# Get the Google Maps API key from the environment
api_key = os.getenv("GOOGLE_MAPS_API_KEY")

st.title("Google Maps Path Generator")

# Input fields for source and destination
src = st.text_input("Enter source address:")
dest = st.text_input("Enter destination address:")

if st.button("Generate Routes"):
    # Use the Google Directions API to get the path with alternatives
    directions_url = f"https://maps.googleapis.com/maps/api/directions/json"
    params = {
        "origin": src,
        "destination": dest,
        "key": api_key,
        "alternatives": "true"  # Request alternate routes
    }

    response = requests.get(directions_url, params=params)
    data = response.json()

    if data.get("status") == "OK":
        # Get and display multiple routes
        coordinates_list = []  # List to store route coordinates

        for idx, route in enumerate(data["routes"]):
            st.subheader(f"Route {idx + 1}:")
            st.write(f"Distance: {route['legs'][0]['distance']['text']}")
            st.write(f"Duration: {route['legs'][0]['duration']['text']}")
            st.write("Instructions:")
            for step in route['legs'][0]['steps']:
                st.write(step['html_instructions'])
            st.write("\n")

            # Extract the polyline string from the response
            polyline_str = route["overview_polyline"]["points"]

            # Decode the polyline to get the coordinates
            coordinates = polyline.decode(polyline_str)

            # Append coordinates to the list
            coordinates_list.append(coordinates)

        # Combine all route coordinates into a single DataFrame
        combined_coordinates = [coord for coords in coordinates_list for coord in coords]
        df = pd.DataFrame(combined_coordinates, columns=["LATITUDE", "LONGITUDE"])

        # Display the path with all routes on the map
        st.map(df)
    else:
        st.error("Error: Unable to generate the paths. Please check your input.")
