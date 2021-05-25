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
from flask.views import MethodView
from index import Index
from review import Review
from dotenv import load_dotenv
from flask_googlemaps import GoogleMaps
import os

load_dotenv()


# Create app object
app = flask.Flask(__name__)
MAP_KEY = os.getenv('MAP_KEY')
app.config['GOOGLEMAPS_KEY'] = MAP_KEY
GoogleMaps(app)

app.add_url_rule('/',
                 view_func=Index.as_view('index'),
                 methods=["GET", 'POST'])

app.add_url_rule('/reviews/',
                 view_func=Review.as_view('review'),
                 methods=['POST'])





if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
