from pymongo import MongoClient
from config import Config
import logging

class Database:
    _db = None
    
    @classmethod
    def initialize(cls):
        try:
            client = MongoClient(Config.MONGODB_URI)
            cls._db = client.get_default_database()
            # Test connection
            cls._db.command('ping')
            logging.info("Database connected successfully")
        except Exception as e:
            logging.error(f"Database connection failed: {e}")
            raise
    
    @classmethod
    def get_database(cls):
        if cls._db is None:
            cls.initialize()
        return cls._db
    
    @classmethod
    def get_collection(cls, collection_name):
        return cls.get_database()[collection_name]