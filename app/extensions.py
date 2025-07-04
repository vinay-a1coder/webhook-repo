from flask_pymongo import PyMongo

import os
from dotenv import load_dotenv
from pymongo import MongoClient
from datetime import datetime

load_dotenv()

class Config:
    MONGODB_URI = os.environ.get('MONGODB_URI', 'mongodb://localhost:27017/webhook_db')
    SECRET_KEY = os.environ.get('SECRET_KEY', 'your-secret-key-here')
    DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'


class WebhookDB:
    def __init__(self):
        self.client = MongoClient(os.environ.get('MONGODB_URI', 'mongodb://localhost:27017/'))
        self.db = self.client.webhook_db
        self.collection = self.db.github_events
    
    def insert_event(self, event_data):
        """Insert a new GitHub event into the database"""
        try:
            result = self.collection.insert_one(event_data)
            return result.inserted_id
        except Exception as e:
            print(f"Error inserting event: {e}")
            return None
    
    def get_latest_events(self, limit=20):
        """Get the latest events from the database"""
        try:
            events = list(self.collection.find().sort("timestamp", -1).limit(limit))
            return events
        except Exception as e:
            print(f"Error fetching events: {e}")
            return []
    
    def close_connection(self):
        """Close the database connection"""
        self.client.close()