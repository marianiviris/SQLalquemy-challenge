from flask import Flask, jsonify
import numpy as np
import pandas as pd
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect
import datetime

app = Flask(__name__)

engine = create_engine("sqlite:///hawaii.sqlite", connect_args={'check_same_thread': False})

Base = automap_base()
Base.prepare(engine, reflect=True)

Measurement = Base.classes.measurement
Station = Base.classes.station

session = Session(engine)

@app.route("/")
def home():
    print("Server received request for 'Home' page...")

    # List all routes that are available
    return ("Welcome to Climate App!<br/>"
        f"Available Routes:<br/><br/>"
        f"/api/v1.0/precipitation<br/>"
        f"-the dates and precipitation observations from the last year<br/><br/>"
        f"/api/v1.0/stations<br/>"
        f"- list of stations from the dataset<br/><br/>"
        f"/api/v1.0/tobs<br/>"
        f"- list of Temperature Observations (tobs) for the previous year<br/><br/>"
        f"/api/v1.0/calc_temps/<start><br/>"
        f"- list of `TMIN`, `TAVG`, and `TMAX` for all dates greater than and equal to the start date<br/><br/>"
        f"/api/v1.0/calc_temps/<start>/<end><br/>"
        f"- the `TMIN`, `TAVG`, and `TMAX` for dates between the start and end date inclusive<br/><br/>")



@app.route("/api/v1.0/precipitation")
def precipitation():
# Convert the query results to a Dictionary using date as the key and prcp as the value.
# Return the JSON representation of your dictionary.

    prcp_r = session.query(Measurement.date, Measurement.prcp)

    precipitation = {item.date: item.prcp for item in prcp_r}

    return jsonify(precipitation)

@app.route("/api/v1.0/stations")
def stations():
    # Return a JSON list of stations from the dataset.
    station_r = session.query(Station.station, Station.name).group_by(Station.station)
    station_l = list(np.ravel(station_r))
    return jsonify(station_l)

@app.route("/api/v1.0/tobs")
def tobs():
    # Query for the dates and temperature observations from a year from the last data point.
    # Return a JSON list of Temperature Observations (tobs) for the previous year.
    tobs_r = session.query(Measurement.date, Measurement.tobs).filter(Measurement.date.\
            between('2016-08-23', '2017-08-23'))
    
    tobs_l = {item.date: item.tobs for item in tobs_r}
    
    return jsonify(tobs_l)


@app.route("/api/v1.0/calc_temps/<start>")
def start_date(start):
    # Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start date.
    # When given the start only, calculate TMIN, TAVG, and TMAX for all dates greater than and equal to the start date.
    start = datetime.datetime.strptime(start, "%Y-%m-%d").date()
    start_r = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start)
    start_tobs = {"Tmin": start_r[0][0], "Tavg": start_r[0][1], "Tmax": start_r[0][2]}
    return jsonify(start_tobs)

@app.route("/api/v1.0/calc_temps/<start>/<end>")
def start_end_date(start, end):
    # Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.
    # When given the start and the end date, calculate the TMIN, TAVG, and TMAX for dates between the start and end date inclusive.
    start1 = datetime.datetime.strptime(start, "%Y-%m-%d").date()
    end1 = datetime.datetime.strptime(end, "%Y-%m-%d").date()
    start_end_r = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date.between(start1, end1))
    start_end_tobs = {"Tmin": start_end_r[0][0], "Tavg": start_end_r[0][1], "Tmax": start_end_r[0][2]}
    return jsonify(start_end_tobs)

@app.route("/about")
def about():
    print("Server received request for 'About' page...")
    return "Welcome to my 'About' page!"


if __name__ == "__main__":
    app.run(debug=True)