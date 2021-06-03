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
        super.__init__(apiKey)
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
        self.searchBusinesses(location,searchTerm)
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
