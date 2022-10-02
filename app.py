import sqlite3
from unittest import result
import requests
from tqdm import tqdm
import json 
import numpy as np
import pandas as pd
from flask import Flask, request


app = Flask("API CAPSTONE BANI") 

@app.route('/')
@app.route('/homepage')
def home():
    return 'Hello World, welcome to Capstone API Project by Bani'

#Route for Stations#

@app.route('/stations/')
def route_all_stations():
    conn = make_connection()
    stations = get_all_stations(conn)
    return stations.to_json()

@app.route('/stations/<station_id>')
def route_stations_id(station_id):
    conn = make_connection()
    station = get_station_id(station_id, conn)
    return station.to_json()

#Route for Trips
@app.route('/trips/')
def route_all_trips():
    conn = make_connection()
    trips = get_all_trips(conn)
    return trips.to_json()

@app.route('/trips/<trip_id>')
def route_trips_id(trip_id):
    conn = make_connection()
    trips = get_trip_id(trip_id, conn)
    return trips.to_json()

@app.route('/trips/average_duration') 
def route_trips_average():
    conn = make_connection()
    query = f"SELECT * FROM trips"
    selected_data = pd.read_sql_query(query, conn)
# Make the aggregate
    result = selected_data.groupby('subscriber_type').agg({
    'duration_minutes' : 'mean'
    })
# Return the result
    return result.to_json()

@app.route('/trips/average_duration/<bike_id>') 
def route_trips_average_bike_id(bike_id): 
    conn = make_connection()
    query = f"SELECT * FROM trips WHERE bikeid = {bike_id}"
    selected_data = pd.read_sql_query(query, conn)
# Make the aggregate
    result = selected_data.groupby('subscriber_type').agg({
    'duration_minutes' : 'mean'
    })
# Return the result
    return result.to_json()

@app.route('/trips/period/<period>') 
def route_stations_period(period): 
    conn = make_connection()
    query = f"SELECT * FROM trips WHERE start_time LIKE('{period}%')"
    selected_data = pd.read_sql_query(query, conn)

# Make the aggregate
    result = selected_data.groupby('start_station_id').agg({
    'bikeid' : 'count',
    'duration_minutes' : 'mean'
    })
# Return the result
    return result.to_json()

#route post

@app.route('/json', methods=['POST']) 
def json_example():

    req = request.get_json(force=True) # Parse the incoming json data as Dictionary

    name = req['name']
    age = req['age']
    address = req['address']

    return (f'''Hello {name}, your age is {age}, and your address in {address}
            ''')

@app.route('/stations/add', methods=['POST']) 
def route_add_station():
    # parse and transform incoming data into a tuple as we need 
    data = pd.Series(eval(request.get_json(force=True)))
    data = tuple(data.fillna('').values)

    conn = make_connection()
    result = insert_into_stations(data, conn)
    return result


@app.route('/trips/add', methods=['POST']) 
def route_add_trip():
    # parse and transform incoming data into a tuple as we need 
    data = pd.Series(eval(request.get_json(force=True)))
    data = tuple(data.fillna('').values)

    conn = make_connection()
    result = insert_into_trips(data, conn)
    return result



######## FUNCTION #########


def get_all_stations(conn):
    query = f"""SELECT * FROM stations"""
    result = pd.read_sql_query(query, conn)
    return result

def get_station_id(station_id, conn):
    query = f"""SELECT * FROM stations WHERE station_id = {station_id}"""
    result = pd.read_sql_query(query, conn)
    return result 

def get_all_trips(conn):
    query = f"""SELECT * FROM trips"""
    result = pd.read_sql_query(query,conn)
    return result

def get_trip_id(trip_id, conn):
    query = f"""SELECT * FROM trips WHERE id = {trip_id}"""
    result=pd.read_sql_query(query,conn)
    return result

def make_connection():
    connection = sqlite3.connect('austin_bikeshare.db')
    return connection

def insert_into_stations(data, conn):
    query = f"""INSERT INTO stations values {data}"""
    try:
        conn.execute(query)
    except:
        return 'Error'
    conn.commit()
    return 'OK'

def insert_into_trips(data_trip, conn):
    query = f"""INSERT INTO trips values {data_trip}"""
    try:
        conn.execute(query)
    except:
        return 'Error'
    conn.commit()
    return 'OK'

if __name__ == '__main__':
    app.run(debug=True, port=5001)