from flask import redirect, request, url_for, render_template
from flask.views import MethodView
from google.cloud import language
from api import Yelp, GoogleNLP
import time
import sys
import os
import json
import gbmodel

YELP_API_KEY = os.getenv('YELP_API_KEY')
MAP_KEY = os.getenv('MAP_KEY')
RESULT_AMOUNT = 3


class Review(MethodView):
    def post(self):
        """
        Accepts POST requests, processes the form, retrieves from cache if possible
        else:
            it gets reviews from YELP API based on form data
            puts these reviews for each resturant recieved through google NLP, results mentioning food entered
            by user are saved.
            These results are sorted in DESC order by sentiment score and sent to the Google Maps api to construct a 
            map and this map is sent to the render_template() fucncition along with the list of the resturants to display
            to the user.
            The results are saved to cloud datastore along with the qeury that lead to them for subsequent searches

        :returns: Failure or success on rendered_template of review.html
        """
  
        result = request.form
        u_location = result['user_location']
        food = result['food']

        model = gbmodel.get_model()
        
        # Query the cache to see if this search has been done before
        table_results = model.used_before(u_location, food)

        if len(table_results) == 0:

            yelp = Yelp(YELP_API_KEY)
            review_business_list = yelp.getReviews(u_location, food)                

            googleNLP = GoogleNLP()
            googleNLP.sentiment_analysis(review_business_list,food)

            top_businesses = googleNLP.get_top_sentiments(RESULT_AMOUNT)

            # Storing new search in database
            model.insert_results(u_location,food,top_businesses)
        # Or else we retrive from the cache in Datastore
        else:
            top_businesses = []
            print("else statement")
            for item in table_results:
                top_businesses.append([item['name'],item['lat'],item['lon'],item['sent'],])
            
            print("RETRIEVED FROM CACHE")
            top_businesses = self.sort_tuples(top_businesses, 3)
            print(top_businesses)

        ## Send data to review.html and render it
        return render_template('review.html', result=result,top=top_businesses, map=map, key=MAP_KEY)
    
    def sort_tuples(self, sentiment_list, n):
        """
        Gets the top_businesses n resturants based on their NLP sentiment score, in DESC order.
        """
        sentiment_list.sort(key = lambda x: x[3] ,reverse=True)
        return sentiment_list[:n]
