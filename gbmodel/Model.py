class Model():
    """Abstract base class that gets used by model_datastore"""
    def select(self):
        """
        Gets all entries from the database
        :return: Tuple containing all rows of database
        """
        pass

    def insert(self):
        """
        Inserts entry into database. Abstract Base Class
        :raises: Database errors on connection and insertion
        """
        pass
