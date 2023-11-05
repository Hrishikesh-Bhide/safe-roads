import streamlit as st
import requests
from dotenv import load_dotenv
import os
import polyline
import pandas as pd
from resource.constants import logo_path, ohio_accident_dataset, ohio_hospital_dataset_csv
import numpy as np

def color_accident_no(val, q1, median, q3):

    if int(val) >= q3:
        return f'background-color: {"orange"}'
    elif int(val) >= median:
        return f'background-color: {"yellow"}'
    elif int(val) <= q1:
        return f'background-color: {"#00FF00"}'

# Load environment variables from .env file
load_dotenv()

st.set_page_config(page_title="Safe Roads", page_icon="🤖", layout="wide")

# Get the Google Maps API key from the environment
api_key = os.getenv("GOOGLE_MAPS_API_KEY")

ohio_accident_dataset = pd.read_csv(ohio_accident_dataset, nrows=600)
dataset_start_Lat = [round(acc,2) for acc in list(ohio_accident_dataset['Start_Lat'])]
dataset_start_Lng = [round(acc,2) for acc in list(ohio_accident_dataset['Start_Lng'])]

actual_dataset_start_Lat = [acc for acc in list(ohio_accident_dataset['Start_Lat'])]
actual_dataset_start_Lng = [acc for acc in list(ohio_accident_dataset['Start_Lng'])]

ohio_hospital_dataset = pd.read_csv(ohio_hospital_dataset_csv)
hospital_lat = ohio_hospital_dataset['LATITUDE']
hospital_lng = ohio_hospital_dataset['LONGITUDE']


with st.sidebar:
    st.markdown("<h1 style='text-align: center; color: blue;font-size: 30px;'>Safe Roads</h1>", unsafe_allow_html=True)
    st.image(logo_path, width=250)
    # Centered image with custom CSS
    src = st.text_input("Enter Source")
    dest = st.text_input("Enter Destination")

    find_safe_route = st.button("Get the safe route")

if find_safe_route == True:
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

    whole_accident_dataframe = []
    for i in range(len(data["routes"])):
        accident_dataframe = {}
        accident_dataframe["Route No"] = 0
        #accident_dataframe["Co-ordinates"] = []
        accident_dataframe["No Of Accidents"] = 0
        accident_dataframe["Description"] = ""


    if data.get("status") == "OK":
        # Get and display multiple routes
        coordinates_list = []  # List to store route coordinates

        route_color = []
        for idx, route in enumerate(data["routes"]):
            whole_accident_cordinates = []
            # Extract the polyline string from the response
            polyline_str = route["overview_polyline"]["points"]

            # Decode the polyline to get the coordinates
            coordinates = polyline.decode(polyline_str)
            route_lat = []
            route_lag = []
            for cor in coordinates:
                #route_color.append(color_list[idx])
                if dataset_start_Lat.__contains__(round(cor[0],2)) == True:
                    accident_lat_index = dataset_start_Lat.index(round(cor[0],2))
                    if dataset_start_Lng[accident_lat_index] == round(cor[1],2):
                        whole_accident_cordinates.append(cor)

            accident_dataframe = {}
            accident_dataframe["Route No"] = "Route " + str(idx+1)
            #accident_dataframe["Co-ordinates"] = whole_accident_cordinates
            accident_dataframe["No Of Accidents"] = str(len(whole_accident_cordinates))

            whole_accident_dataframe.append(accident_dataframe)

            # Append coordinates to the list
            coordinates_list.append(coordinates)

        # Combine all route coordinates into a single DataFrame
        combined_coordinates = [coord for coords in coordinates_list for coord in coords]

        # Adding Accident Spots
        for lat, lng in zip(actual_dataset_start_Lat, actual_dataset_start_Lng):
            combined_coordinates.append((lat, lng))

        # Adding Hospital Spots
        for lat, lng in zip(hospital_lat, hospital_lng):
            combined_coordinates.append((lat, lng))

        df = pd.DataFrame(combined_coordinates, columns=["LATITUDE", "LONGITUDE"])

        whole_accident_dataframe = pd.DataFrame(whole_accident_dataframe)
        no_accident_list = [int(no) for no in list(whole_accident_dataframe['No Of Accidents'])]
        q1 = np.percentile(no_accident_list, 25)
        median = np.percentile(no_accident_list, 50)
        q3 = np.percentile(no_accident_list, 75)
        sorted_df_descending = whole_accident_dataframe.sort_values(by='No Of Accidents', ascending=True)
        styled_accident_numbers_df = sorted_df_descending.style.applymap(lambda x: color_accident_no(x, q1, median, q3),subset='No Of Accidents')

        route_color_map = {}

        for k in range(len(whole_accident_dataframe['No Of Accidents'])):
            if int(whole_accident_dataframe['No Of Accidents'][k]) <= q1:
                route_color_map[whole_accident_dataframe['Route No'][k]] = '#00FF00' #Green
            elif int(whole_accident_dataframe['No Of Accidents'][k]) <= median:
                route_color_map[whole_accident_dataframe['Route No'][k]] = '#FFFF00' #Yellow
            elif int(whole_accident_dataframe['No Of Accidents'][k]) >= q3:
                route_color_map[whole_accident_dataframe['Route No'][k]] = '#FFA500' #Orange

        route_color_as_per_level = []
        for idx, route in enumerate(data["routes"]):
            polyline_str = route["overview_polyline"]["points"]

            # Decode the polyline to get the coordinates
            coordinates = polyline.decode(polyline_str)
            route_lat = []
            route_lag = []
            for cor in coordinates:
                current_route_color = route_color_map["Route " +str(idx+1)]
                route_color_as_per_level.append(current_route_color)

        # Adding colors for accident spots
        for lat, lng in zip(actual_dataset_start_Lat, actual_dataset_start_Lng):
            route_color_as_per_level.append('#FF0000') # Red

        # Adding colors for hospital Spots
        for lat, lng in zip(hospital_lat, hospital_lng):
            route_color_as_per_level.append('#0000FF') # Blue

        df['Color'] = route_color_as_per_level

        # Display the path with all routes on the map
        st.map(df, color="Color")

        # Create a sample DataFrame
        data = {
            'Color': ['#FFA500', '#FFFF00', '#00FF00', '#FF0000', '#0000FF'],
            'Road Condition': ['Dangerous Route', 'Modarate Risk Route', 'Safe Route', 'Accident Prone Area', 'Hospital']
        }

        df = pd.DataFrame(data)

        # Define a custom function to apply cell background color
        def apply_color(val):
            background_color = f'background-color: {val}'
            return background_color

        # Apply the custom function to style the DataFrame
        styled_df = df.style.applymap(apply_color, subset=['Color'])

        col1, col2 = st.columns(2)

        with col1:
            # Render the styled DataFrame with cell background colors
            st.subheader("Analysis of Risky Roads")
            st.write(styled_accident_numbers_df)
        with col2:
            st.subheader("Color Guidelines")
            st.dataframe(styled_df, use_container_width=True)
    else:
        st.error("Error: Unable to generate the paths. Please check your input.")
