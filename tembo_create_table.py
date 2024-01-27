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


def create_tables(cur):
    try:
        # Test Query
        cur.execute("CREATE TABLE Accident_Original(acc_id INT PRIMARY KEY, Start_Lat FLOAT, Start_Lng FLOAT)")
        cur.execute("CREATE TABLE Accident_Round (acc_id INT PRIMARY KEY, Start_Lat FLOAT, Start_Lng FLOAT)")
        cur.execute("CREATE TABLE Hospital_Original (hospital_id INT PRIMARY KEY, Start_Lat FLOAT, Start_Lng FLOAT)")
    except Exception as e:
        print(f"An error occurred while creating tables: {e}")


def insert_data(cur):
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
    except Exception as e:
        print(f"An error occurred during data insertion: {e}")


def fetch_data(cur):
    try:
        cur.execute("Select * From Accident_Round")
        accident_output = cur.fetchall()
        print("Accident Data:")
        print(accident_output)

        cur.execute("Select * From Hospital_Original")
        hospital_output = cur.fetchall()
        print("Hospital Data:")
        print(hospital_output)
    except Exception as e:
        print(f"An error occurred during data fetching: {e}")


if __name__ == "__main__":
    conn_str = 'postgresql://postgres:cq1bzqXnNuMNrF0s@org-zenith-inst-safe-roads.data-1.use1.tembo.io:5432/postgres'
    conn = connect_to_database(conn_str)

    if conn:
        try:
            # Create a new cursor object.
            cur = conn.cursor()

            # Create tables
            create_tables(cur)

            # Insert data
            insert_data(cur)

            # Fetch data
            fetch_data(cur)

        except Exception as e:
            print(f"An error occurred: {e}")
        finally:
            # Close communication with the database
            cur.close()
            conn.close()
