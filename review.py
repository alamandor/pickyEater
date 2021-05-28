from flask import redirect, request, url_for, render_template
from flask.views import MethodView
from yelpapi import YelpAPI
from google.cloud import language
import time
import sys
import os
import json
import gbmodel

YELP_API_KEY = os.getenv('YELP_API_KEY')
MAP_KEY = os.getenv('MAP_KEY')


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
        yelp_api = YelpAPI(YELP_API_KEY)
        business_ids = []
        review_business_list = []

        result = request.form
        u_location = result['user_location']
        food = result['food']

        model = gbmodel.get_model()
        
        # Query the cache to see if this search has been done before
        table_results = model.used_before(u_location, food)

        if len(table_results) == 0:

            ## Yelp API query to find business ids based on form data
            # Construct a list of dictionaries to keep restirant data with location and review
            business_matches = yelp_api.search_query(location=u_location, term=food)
            businesses = business_matches['businesses']
            for b_ids in businesses:
                b_dict = {
                'name' : b_ids['name'],
                'rating' : b_ids['rating'],
                'lat' : b_ids['coordinates']['latitude'],
                'long' : b_ids['coordinates']['longitude'],
                'id' : b_ids['id'],
                'reviews': []
                }
                review_business_list.append(b_dict)
                business_ids.append(b_ids['id'])

            # Loop through businesses found in search query
            for b_ids in business_ids:
                # Ran into problems exceeding rate limit
                time.sleep(0.2)
                response = yelp_api.reviews_query(b_ids)

            # Grab just the text from review response from yelp
                reviews = response['reviews']
                for text in reviews:
                    for b in review_business_list:
                        if b['id'] == b_ids:
                            b['reviews'].append(text['text'])

            ## End of Yelp API use

            ## List to store resturants with sentiments
            sentiment_tuple_list = []

            ## Google natural language sentiment anaylsis
            for business in review_business_list:
                b_reviews = business['reviews']

                client = language.LanguageServiceClient()    
                document = language.Document(
                    content=str(b_reviews),
                    type_=language.Document.Type.PLAIN_TEXT,
                )
                response = client.analyze_entity_sentiment(
                    document=document,
                    encoding_type='UTF32',
                )
                highest_sentiment = self.process_sentiments_with_resturants(response, business['id'], business['name'], food)
                sentiment_with_resturant = (business['name'], business['lat'], business['long'], highest_sentiment)
                # print(sentiment_with_resturant)
                sentiment_tuple_list.append(sentiment_with_resturant)
            ## End of natural language API use

            # Sort sentiments with resturant info in DESC order
            top = self.sort_tuples(sentiment_tuple_list,3)
            print("MADE THROUGH API CALLS")
            print(top)

            # Storing new search in database
            model.insert(u_location, food, top[0][0],top[0][1],top[0][2],top[0][3])
            model.insert(u_location, food, top[1][0],top[1][1],top[1][2],top[1][3])
            model.insert(u_location, food, top[2][0],top[2][1],top[2][2],top[2][3])
        
        # Or else we retrive from the cache in Datastore
        else:
            top = []
            print("else statement")
            for item in table_results:
                top.append([item['name'],item['lat'],item['lon'],item['sent'],])
            
            print("RETRIEVED FROM CACHE")
            top = self.sort_tuples(top, 3)
            print(top)

        ## Send data to review.html and render it
        return render_template('review.html', result=result,top=top, map=map, key=MAP_KEY)
    
    def process_sentiments_with_resturants(self, sentiment_response, resturant_id, resturant_name, food):
        """
        Goes through the entities and sentiments from google NLP and combines the scores and the maginitudes of 
        entities that mention the user-provided food, and retrieves the entity with the highest score.
        """
        highest = 0.0
        for entity in sentiment_response.entities:
            # Get the aggregate sentiment expressed for this entity in the provided document.
            sentiment = entity.sentiment
            magnitude = sentiment.magnitude
            score = sentiment.score
            combined_score = score*magnitude
            if combined_score > highest and entity.name == food:
                highest = combined_score
                # print(u"resturant name: {}".format(resturant_name))
                # print(u"resturant ID: {}".format(resturant_id))
                # print(u"Representative name for the entity: {}".format(entity.name))
                # print(u"Entity sentiment score: {}".format(sentiment.score))
                # print(u"Entity sentiment magnitude: {}".format(sentiment.magnitude))
        
        return highest
    
    def sort_tuples(self, sentiment_list, n):
        """
        Gets the top n resturants based on their NLP sentiment score, in DESC order.
        """
        sentiment_list.sort(key = lambda x: x[3] ,reverse=True)
        return sentiment_list[:n]
