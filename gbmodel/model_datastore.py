from .Model import Model
from datetime import datetime
from google.cloud import datastore

def from_datastore(entity):
    """Translates Datastore results into the format expected by the
    application.

    Datastore typically returns:
        [Entity{key: (kind, id), prop: val, ...}]

    This returns:
        [ location, food, name, lat, long, sentiment]
    """
    if not entity:
        return None
    if isinstance(entity, list):
        entity = entity.pop()
    return [entity['location'],entity['food'],entity['name'], entity['lat'],entity['lon'],entity['sent']]

class model(Model):
    def __init__(self):
        self.client = datastore.Client('picky-eater-aag3')

    def select(self):
        query = self.client.query(kind = 'picky-eater-aag3') # was 'review'
        entities = list(map(from_datastore,query.fetch()))
        return entities

    def insert(self,location,food,name,lat,lon,sent):
        key = self.client.key('picky-eater-aag3')
        rev = datastore.Entity(key)
        rev.update( {
            'location': location.lower(),
            'food' : food.lower(),
            'name' : name.lower(),
            'lat' : lat,
            'lon' : lon,
            'sent' : sent
            })
        self.client.put(rev)
        return True
    def insert_results(self, location, search_term, businesses):
        for x in range(len(businesses)):
            self.insert(location, search_term, businesses[x][0], businesses[x][1], businesses[x][2], businesses[x][3])
           
    def used_before(self,location, food):
        """
        Queries the database to see if this search has been done before.

        Returns results of query as a list since datastore instead gives you an iterator object
        """
        query = self.client.query(kind="picky-eater-aag3")
        query.add_filter("location", "=", location.lower())
        query.add_filter("food", "=", food.lower())
        res = query.fetch()
        return list(res)
