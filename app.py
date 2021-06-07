"""
A Flask App to manage a database of charities.
Keeps track of the Name, Address, Email, Whether it is a Non-Profit or not, notes regarding the specific charity and its Phone Number

Listens on port 5000

Adds 3 different routes once instantiated:
1. Root (/): Homepage
2. /sign: page to enter info into table
3. /view: View existing entries in browser from database

"""
import flask
from flask import render_template, redirect
from flask.views import MethodView
import logging
from google.cloud import logging as glogging
from googleapiclient.errors import HttpError
from index import Index
from review import Review
from yelpapi import YelpAPI
import os
# Instantiates a client
logging_client = glogging.Client()

# The name of the log to write to
log_name = "app-log"
# Selects the log to write to
Glogger = logging_client.logger(log_name)




# Create app object
app = flask.Flask(__name__)
logging.basicConfig(filename='/var/log/record.log', level=logging.ERROR, format=f'%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s')
LOG = flask.logging.create_logger(app)
@app.errorhandler(Exception)
def internal_error_handler(e):
    if isinstance(e,YelpAPI.YelpAPIError):
        LOG.error("YELP API ERROR: " + str(e))
        # Writes the log entry
        Glogger.log_text("YELP API ERROR: " + str(e), severity="ERROR")
        return render_template('index.html'), 500
    if isinstance(e,HttpError):
        LOG.error("Google NLP API ERROR: " + str(e))
        Glogger.log_text("GOOGLE API ERROR: " + str(e), severity="ERROR")
        return render_template('index.html'), 500
    else:
        LOG.error("INTERAL ERROR: " + str(e))
        return render_template('index.html'), 500        


# app.register_error_handler(500, internal_error_handler)

app.add_url_rule('/',
                 view_func=Index.as_view('index'),
                 methods=["GET", 'POST'])

app.add_url_rule('/reviews/',
                 view_func=Review.as_view('review'),
                 methods=['POST', 'GET'])


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
