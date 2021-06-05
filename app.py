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
from index import Index
from review import Review
import os

# Create app object
app = flask.Flask(__name__)


def internal_error_handler(e):
    return render_template('index.html', err=e), 500


app.register_error_handler(500, internal_error_handler)

app.add_url_rule('/',
                 view_func=Index.as_view('index'),
                 methods=["GET", 'POST'])

app.add_url_rule('/reviews/',
                 view_func=Review.as_view('review'),
                 methods=['POST', 'GET'])


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
