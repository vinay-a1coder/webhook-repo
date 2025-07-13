import os
import logging
import logging.handlers
from functools import wraps
from flask import request

def setup_logging(app):
    
    # Create logs directory if it doesn't exist
    if not os.path.exists('logs'):
        os.makedirs('logs')
    
    # Configure logging format
    log_format = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Setup file handler with rotation
    file_handler = logging.handlers.RotatingFileHandler(
        'logs/webhook.log',
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    file_handler.setFormatter(log_format)
    file_handler.setLevel(logging.INFO)
    
    # Setup error file handler
    error_handler = logging.handlers.RotatingFileHandler(
        'logs/error.log',
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    error_handler.setFormatter(log_format)
    error_handler.setLevel(logging.ERROR)
    
    # Setup console handler for development
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(log_format)
    console_handler.setLevel(logging.DEBUG)
    
    # Configure app logger
    app.logger.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.addHandler(error_handler)
    app.logger.addHandler(console_handler)
    
    # Remove default Flask handler to avoid duplicate logs
    app.logger.handlers = [file_handler, error_handler, console_handler]
    
    return app.logger

def log_request_info(f):
    """Decorator to log request information"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Get logger from current app context
        logger = logging.getLogger(__name__)
        
        logger.info(f"Request: {request.method} {request.url}")
        logger.info(f"Remote addr: {request.remote_addr}")
        
        try:
            response = f(*args, **kwargs)
            logger.info(f"Response: {response.status_code if hasattr(response, 'status_code') else 'Success'}")
            return response
        except Exception as e:
            logger.error(f"Error in {f.__name__}: {str(e)}", exc_info=True)
            raise
    
    return decorated_function