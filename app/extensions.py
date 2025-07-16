from flask_pymongo import PyMongo
import logging
import os
from dotenv import load_dotenv
from pymongo import MongoClient
from datetime import datetime, timedelta, timezone

load_dotenv()

logger = logging.getLogger(__name__)

class Config:
    MONGODB_URI = os.environ.get('MONGODB_URI', 'mongodb://localhost:27017/webhook_db')
    SECRET_KEY = os.environ.get('SECRET_KEY', 'your-secret-key-here')
    DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'


class WebhookDB:
    def __init__(self):
        logger.info("Initializing database connection...")
        self.client = MongoClient(os.environ.get('MONGODB_URI', 'mongodb://localhost:27017/'))
        self.db = self.client.webhook_db
        self.collection = self.db.github_events

        self.client.admin.command('ping')
        logger.info("Database connection established successfully")
    
    def insert_event(self, event_data):
        """Insert a new GitHub event into the database"""
        try:
            logger.info(f"Inserting event: {event_data.get('action', 'unknown')} by {event_data.get('author', 'unknown')}")
            
            result = self.collection.insert_one(event_data)
            if result.inserted_id:
                logger.info(f"Event inserted successfully with ID: {result.inserted_id}")
                return result.inserted_id
            else:
                logger.error("Event insertion failed - no ID returned")
                return None
            
        except Exception as e:
            logger.error(f"Error inserting event: {e}", exc_info=True)
            return None
    
    def get_latest_events(self, seconds=15):
        """Get events from the last N seconds"""
        try:
            logger.info(f"Fetching events from the last {seconds} seconds...")
            
            # Calculate the cutoff time in UTC to match stored timestamps
            cutoff_time = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(seconds=seconds)
            
            events = list(self.collection.find(
                {"timestamp": {"$gte": cutoff_time}}, 
                {"_id": 0}
            ).sort("timestamp", -1))
            
            logger.info(f"Successfully retrieved {len(events)} events from the last {seconds} seconds")
            return events
            
        except Exception as e:
            logger.error(f"Error fetching recent events: {e}", exc_info=True)
            return []
    
    def close_connection(self):
        """Close the database connection"""
        try:
            logger.info("Closing database connection...")
            self.client.close()
            logger.info("Database connection closed successfully")
        except Exception as e:
            logger.error(f"Error closing database connection: {e}", exc_info=True)