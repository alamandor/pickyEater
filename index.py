"""
Backend code for the homepage, simply renders index.html as this is just a static landing page
"""
from flask import redirect, request, url_for, render_template
from flask.views import MethodView


class Index(MethodView):
    """
    Driver function to render the homepage for site
    """
    def get(self):
        """
        Single method to render the index.html page.
        """

        return render_template('index.html')
    def post(self):
        """
        Accepts POST requests, sends the process to the code to do the API calls and process them
        along with user data entered in form.

        :returns: Failure or success on Redirect() function
        """

        return redirect(url_for('review'))
