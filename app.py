# Import the dependencies.
import numpy as np
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify
from collections import OrderedDict

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)
# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station
# Create our session (link) from Python to the DB
session = Session(engine)
#################################################
# Flask Setup
#################################################
app = Flask(__name__)

@app.route("/")
def welcome():
    return (
        f"<html>"
        f"<head>"
        f"<title>Challenge Module 10: Part 2</title>"
        f"<style>"
        f"body {{ background-color: turquoise; color: white; }}"
        f"</style>"
        f"</head>"
        f"<body>"
        f"<center>"
        f"<h1>Welcome to the Climate App API!</h1>"
        f"<h1>Surf's Up<img width='600' src='https://a.cdn-hotels.com/gdcs/production186/d559/a82dee28-b6fd-417c-b51b-a535ddeb2f85.jpg?impolicy=fcrop&w=1600&h=1066&q=medium'/ >Bruh!</h1><h1>Step 2 - Climate App</h1>"
        f"</center>"
        f"<h2>Available Routes:</h2>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start<br/>"
        f"/api/v1.0/start/end<br/>"
        f"<h2>But clicking on HYPERLINKS is so MUCH easier:</h2>"
        f"<ol><li><a href='http://127.0.0.1:5000/api/v1.0/precipitation' target='_blank'>/api/v1.0/precipitation</a></li><br/>"
        f"<li><a href='http://127.0.0.1:5000/api/v1.0/stations' target='_blank'>/api/v1.0/stations</a></li><br/>"
        f"<li><a href='http://127.0.0.1:5000/api/v1.0/tobs' target='_blank'>/api/v1.0/tobs</a></li><br/>"
        f"<li><a href='http://127.0.0.1:5000/api/v1.0/2016-09-06' target='_blank'>/api/v1.0/2016-09-06</a></li><br/>"
        f"<li><a href='http://127.0.0.1:5000/api/v1.0/2015-12-25/2017-01-01' target='_blank'>/api/v1.0/2015-12-25/2017-01-01</a></li>"
        f"</ol>"
        f"</body>"
        f"</html>"
    ), 200 
 # 200 is the status code for OK

@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)
    start_date = '2016-08-23'
    end_date = '2017-08-23'
    precipitation_results = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= start_date, Measurement.date <= end_date).all()
    session.close()

      # Convert the list to Dictionary
    all_precipitation = [{"date": date, "prcp": prcp} for date, prcp in precipitation_results]

    return jsonify(all_precipitation)

@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    # Query to retrieve all station data
    stations_data = session.query(Station.name, Station.station, Station.elevation, Station.latitude, Station.longitude).all()
    session.close()

    # Format the results as a list of dictionaries
    stations_results = [{"name": name, "station": station, "elevation": elevation, "latitude": latitude, "longitude": longitude}\
                    for name, station, elevation, latitude, longitude in stations_data]

    ordered_stations_results = [OrderedDict(sorted(station_info.items(), key=lambda\
                                                    item: ["name", "station", "elevation", "latitude", "longitude"].index(item[0]))) for station_info in stations_results]

    return jsonify(ordered_stations_results)

@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)
    start_date = '2016-08-23'
    end_date = '2017-08-23'
    top_station = session.query(Measurement.station).\
                    group_by(Measurement.station).\
                    order_by(func.count(Measurement.station).desc()).subquery()
    
    tobs_results = session.query(Measurement.date, Measurement.tobs).\
                filter(Measurement.date >= start_date, Measurement.date <= end_date).all()
    session.close()

        # Convert the list to Dictionary
    top_tobs_station = [{"date": date, "tobs": tobs} for date, tobs in tobs_results]

    return jsonify(top_tobs_station)

@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def calc_temps(start = None, end = None):
    session = Session(engine)
    
    # Make a list to query (the minimum, average and maximum temperature)
    sel=[func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]
    
    # Find out if there's an end date 
    if end == None: 
        # Query the data from start date to the most recent date
        start_data = session.query(*sel).filter(Measurement.date >= start).all()
        
        # Convert list of tuples into normal list
        start_list = [item for sublist in start_data for item in sublist]
        return jsonify(start_list)
    
    else:
        # Query the data from start date to the end date
        start_end_data = session.query(*sel).filter(Measurement.date >= start).\
            filter(Measurement.date <= end).all()
        # Convert list of tuples into normal list 
        start_end_list = [item for sublist in start_end_data for item in sublist]

        return jsonify(start_end_list)           
    
    session.close()
    
if __name__ == "__main__":
    app.run(debug = True)