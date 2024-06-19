# Import the dependencies.
from datetime import timedelta
import numpy as np
import pandas as pd
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(autoload_with=engine)

inspector = inspect(engine)
print(inspector.get_table_names())

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)



#################################################
# Flask Routes
#################################################
@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end>"
    )
@app.route("/api/v1.0/precipitation")
def precipitation():
    """Convert the query results from your precipitation analysis (i.e. retrieve only the last 12 months of data) to a dictionary using date as the key and prcp as the value."""
    # Find the most recent date in the data set.
    most_recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    most_recent_date
    # Design a query to retrieve the last 12 months of precipitation data and plot the results. 
    # Starting from the most recent data point in the database. 
    most_recent_date_str = most_recent_date[0]

    # Calculate the date one year from the last date in data set.
    most_recent_date_dt = dt.datetime.strptime(most_recent_date_str, '%Y-%m-%d').date()
    one_year_ago = most_recent_date_dt - timedelta(days=365)

    # Perform a query to retrieve the data and precipitation scores
    results = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= one_year_ago).all()
    
    session.close()
    # Create a dictionary using date as the key and prcp as the value
    prcp_data = {date: prcp for date, prcp in results}

    return jsonify(prcp_data)
    


@app.route("/api/v1.0/stations")
def stations():
    """ Return a JSON list of stations from the dataset."""
    # Query all stations
    results = session.query(Station.station).all()
    session.close()
    # Convert list of tuples into normal list
    stations = list(np.ravel(results))

    return jsonify(stations)


@app.route("/api/v1.0/tobs")
def tobs():
    """ Query the dates and temperature observations of the most-active station for the previous year of data."""
    # Find most recent date
    most_recent = session.query(func.max(Measurement.date)).filter(Measurement.station == 'USC00519281').scalar()
    most_recent
    # 12 months before the most recent date of '2017-08-18'
    start_date = '2016-08-18'

    # Query the temperature observation data for station 'USC00519281' within the 12-month period
    results = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.station == 'USC00519281').\
        filter(Measurement.date >= start_date).\
        filter(Measurement.date <= most_recent).all()
    session.close()
     # Create a dictionary using date as the key and prcp as the value
    prcp_data = {date: prcp for date, prcp in results}

    return jsonify(prcp_data)


@app.route("/api/v1.0/<start>")
def start_date_temps(start):
    """Return the min, max, and avg temperatures for dates greater than or equal to the start date."""
    # Query the database to calculate TMIN, TAVG, and TMAX for dates greater than or equal to the start date
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).all()

    session.close()
    # Create a dictionary to store the calculated values
    temp_data = {
        "start_date": start,
        "TMIN": results[0][0],
        "TAVG": results[0][1],
        "TMAX": results[0][2]
    }

    return jsonify(temp_data)


@app.route("/api/v1.0/<start>/<end>")
def calc_temps(start, end):
    """Return a JSON list of the minimum temperature, the average temperature, and the maximum temperature for a specified start or start-end range."""
    # Query the minimum, average, and maximum temperatures for the specified date range
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).\
        filter(Measurement.date <= end).all()

    session.close()

    # Create a dictionary to hold the temperature data
    temp_data = {
        'start_date': start,
        'end_date': end,
        'TMIN': results[0][0],
        'TAVG': results[0][1],
        'TMAX': results[0][2]
    }

    return jsonify(temp_data)


if __name__ == '__main__':
    app.run(debug=True)

