from flask import Flask
from .extensions import Config
from app.webhook.routes import webhook


# Creating our flask app
def create_app():

    app = Flask(__name__)
    app.config.from_object(Config)
    # registering all the blueprints
    app.register_blueprint(webhook)
    
    return app
