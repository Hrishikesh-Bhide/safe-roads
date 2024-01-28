import psycopg2
import pandas as pd
from resource.constants import ohio_hospital_dataset_csv, ohio_accident_dataset_csv

def connect_to_database(conn_str):
    try:
        # Create a new database session
        conn = psycopg2.connect(conn_str)
        return conn
    except Exception as e:
        print(f"Unable to connect to the database: {e}")
        return None

def create_tables(cur, conn):
    try:
        # Test Query
        cur.execute("CREATE TABLE Accident_Original(acc_id INT PRIMARY KEY, Start_Lat FLOAT, Start_Lng FLOAT)")
        cur.execute("CREATE TABLE Accident_Round (acc_id INT PRIMARY KEY, Start_Lat FLOAT, Start_Lng FLOAT)")
        cur.execute("CREATE TABLE Hospital_Original (hospital_id INT PRIMARY KEY, Start_Lat FLOAT, Start_Lng FLOAT)")
        conn.commit()
    except Exception as e:
        print(f"An error occurred while creating tables: {e}")

def insert_data(cur, conn):
    ohio_accident_dataset = pd.read_csv(ohio_accident_dataset_csv, nrows=600)
    actual_dataset_start_Lat = [acc for acc in list(ohio_accident_dataset['Start_Lat'])]
    actual_dataset_start_Lng = [acc for acc in list(ohio_accident_dataset['Start_Lng'])]

    ohio_hospital_dataset = pd.read_csv(ohio_hospital_dataset_csv)
    hospital_lat = ohio_hospital_dataset['LATITUDE']
    hospital_lng = ohio_hospital_dataset['LONGITUDE']

    try:
        i = 0
        for start_lat, start_lng in zip(actual_dataset_start_Lat, actual_dataset_start_Lng):
            cur.execute(
                f"INSERT INTO Accident_Round(acc_id, Start_Lat, Start_Lng) VALUES ({i + 1}, {round(start_lat, 2)}, {round(start_lng, 2)})")
            i += 1

        i = 0
        for start_lat, start_lng in zip(hospital_lat, hospital_lng):
            cur.execute(
                f"INSERT INTO Hospital_Original(hospital_id, Start_Lat, Start_Lng) VALUES ({i + 1}, {start_lat}, {start_lng})")
            i += 1

        print("Data inserted successfully.")
        conn.commit()
    except Exception as e:
        print(f"An error occurred during data insertion: {e}")

def get_accident_data_from_database(cur):
    try:
        cur.execute("SELECT Start_Lat, Start_Lng FROM Accident_Round")
        result = cur.fetchall()
        return result
    except Exception as e:
        print(f"Error retrieving accident data: {e}")
        return []

def get_hospital_data_from_database(cur):
    try:
        cur.execute("SELECT Start_Lat, Start_Lng FROM Hospital_Original")
        result = cur.fetchall()
        return result
    except Exception as e:
        print(f"Error retrieving hospital data: {e}")
        return []