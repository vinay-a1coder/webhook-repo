from flask import Flask
from .extensions import Config
from app.webhook.routes import webhook
from .logging_config import setup_logging


# Creating our flask app
def create_app():

    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Setup logging BEFORE registering blueprints
    setup_logging(app)
    
    # Register blueprints
    app.register_blueprint(webhook)
    
    app.logger.info("Flask application started successfully")
    
    return app
