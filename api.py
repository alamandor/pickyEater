from yelpapi import YelpAPI
from google.cloud import language
import time


class api:
    """Abstract base class that gets used by yelp and google apis"""

    def __init__(self, apiKey):
        """
        Sets the API key
        """
        self.key = apiKey


class Yelp(api):
    def __init__(self, apiKey):
        super().__init__(apiKey)
        self.yelpAPI = YelpAPI(self.key)
        self.businesses_search_results = []
        self.business_ids = []

    def getBusinesses(self):
        return self.businesses_search_results

    def getBusinessIds(self):
        return self.business_ids

    def searchBusinesses(self, location, searchTerm):
        ## Yelp API query to find business ids based on form data
        # Construct a list of dictionaries to keep restirant data with location and review
        business_matches = self.yelpAPI.search_query(
            location=location, term=searchTerm)
        businesses = business_matches['businesses']
        for b_ids in businesses:
            b_dict = {
                'name': b_ids['name'],
                'rating': b_ids['rating'],
                'lat': b_ids['coordinates']['latitude'],
                'long': b_ids['coordinates']['longitude'],
                'id': b_ids['id'],
                'reviews': []
            }
            self.businesses_search_results.append(b_dict)
            self.business_ids.append(b_ids['id'])

    def getReviews(self, location, searchTerm):
        self.searchBusinesses(location, searchTerm)
        # Loop through businesses found in search query
        for b_ids in self.business_ids:
            # Ran into problems exceeding rate limit
            time.sleep(0.2)
            response = self.yelpAPI.reviews_query(b_ids)

            # Grab just the text from review response from yelp
            reviews = response['reviews']
            for text in reviews:
                for b in self.businesses_search_results:
                    if b['id'] == b_ids:
                        b['reviews'].append(text['text'])

        return self.getBusinesses()


class GoogleNLP:
    def __init__(self):
        ## List to store resturants with sentiments
        self.resturants_with_sentiments = []

    def sentiment_analysis(self,businesses,analysis_term):
        for business in businesses:
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
            highest_sentiment = self.process_sentiments_with_resturants(
                response, business['id'], business['name'], analysis_term)
            sentiment_with_resturant = (
                business['name'], business['lat'], business['long'], highest_sentiment)
            # print(sentiment_with_resturant)
            self.resturants_with_sentiments.append(sentiment_with_resturant)

    def process_sentiments_with_resturants(self, sentiment_response, resturant_id, resturant_name, analysis_term):
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
            if combined_score > highest and entity.name == analysis_term:
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
    
    def get_top_sentiments(self, n):
        return self.sort_tuples(self.resturants_with_sentiments,n)
