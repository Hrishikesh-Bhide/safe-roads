import streamlit as st
import requests
from dotenv import load_dotenv
import os
import polyline
import pandas as pd
from resource.constants import logo_path, ohio_accident_dataset, hospital_dataset, ohio_hospital_dataset_csv
import numpy as np

def color_accident_no(val, q1, median, q3):

    if int(val) >= q3:
        return f'background-color: {"orange"}'
    elif int(val) >= median:
        return f'background-color: {"#F9E076"}'
    elif int(val) <= q1:
        return f'background-color: {"green"}'

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

with st.sidebar:
    st.title("Safe Roads")
    st.image(logo_path, width=250)
    src = st.text_input("Enter Source")
    dest = st.text_input("Enter Destination")

    find_safe_route = st.button("Submit")

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

    if data.get("status") == "OK":
        # Get and display multiple routes
        coordinates_list = []  # List to store route coordinates

        color_list = ['#0000FF', '#FFA500', '#00FF00']
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

        for lat, lng in zip(actual_dataset_start_Lat, actual_dataset_start_Lng):
            #route_color.append('#FF0000')
            combined_coordinates.append((lat, lng))

        df = pd.DataFrame(combined_coordinates, columns=["LATITUDE", "LONGITUDE"])
        #df['Color'] = route_color

        # Display the path with all routes on the map
        #st.map(df, color="Color")

        whole_accident_dataframe = pd.DataFrame(whole_accident_dataframe)
        no_accident_list = [int(no) for no in list(whole_accident_dataframe['No Of Accidents'])]
        q1 = np.percentile(no_accident_list, 25)
        median = np.percentile(no_accident_list, 50)
        q3 = np.percentile(no_accident_list, 75)
        styled_accident_numbers_df = whole_accident_dataframe.style.applymap(lambda x: color_accident_no(x, q1, median, q3),subset='No Of Accidents')


        route_color_map = {}

        for k in range(len(whole_accident_dataframe['No Of Accidents'])):
            if int(whole_accident_dataframe['No Of Accidents'][k]) <= q1:
                route_color_map[whole_accident_dataframe['Route No'][k]] = '#00FF00' # Green
            elif int(whole_accident_dataframe['No Of Accidents'][k]) <= median:
                route_color_map[whole_accident_dataframe['Route No'][k]] = '#F9E076' # Yellow
            elif int(whole_accident_dataframe['No Of Accidents'][k]) >= q3:
                route_color_map[whole_accident_dataframe['Route No'][k]] = '#FFA500' #Orange

        #st.write(route_color_map)

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

        for lat, lng in zip(actual_dataset_start_Lat, actual_dataset_start_Lng):
            route_color_as_per_level.append('#FF0000')

        df['Color'] = route_color_as_per_level

        # Display the path with all routes on the map
        st.map(df, color="Color")
        st.write(styled_accident_numbers_df)
        #st.write(route_color_as_per_level)
    else:
        st.error("Error: Unable to generate the paths. Please check your input.")
