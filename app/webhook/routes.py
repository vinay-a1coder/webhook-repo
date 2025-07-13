import logging
from functools import wraps
from flask import Blueprint, json, request, jsonify, render_template
from .utils import parse_webhook_data, db
from app.logging_config import log_request_info

# Setup logger for this module
logger = logging.getLogger(__name__)

webhook = Blueprint('Webhook', __name__)

@webhook.route('/receiver', methods=["POST"])
@log_request_info
def receiver():
    logger.info("Receiver endpoint called")
    return {}, 200

@webhook.route('/')
@log_request_info
def index():
    """Main page displaying GitHub events"""
    logger.info("Index page requested")
    try:
        return render_template('index.html')
    except Exception as e:
        logger.error(f"Error rendering index template: {e}", exc_info=True)
        return jsonify({'error': 'Template rendering failed'}), 500

@webhook.route('/webhook', methods=['POST'])
@log_request_info
def webhooks():
    """Webhook endpoint to receive GitHub events"""
    try:
        payload = request.get_json()
        
        if not payload:
            logger.warning("Received webhook with no payload")
            return jsonify({'error': 'No payload received'}), 400
        
        event_type = request.headers.get('X-GitHub-Event', 'unknown')
        logger.info(f"Received GitHub webhook event: {event_type}")
        
        # Log payload size for monitoring
        payload_size = len(json.dumps(payload))
        logger.info(f"Payload size: {payload_size} bytes")
        
        # Parse the webhook data
        logger.info("Parsing webhook data...")
        event_data = parse_webhook_data(payload)
        
        if event_data:
            logger.info(f"Event parsed successfully: {event_data.get('action', 'unknown')} by {event_data.get('author', 'unknown')}")
            
            # Store in database
            logger.info("Storing event in database...")
            result = db.insert_event(event_data)
            
            if result:
                logger.info(f"Event stored successfully in database")
                return jsonify({'status': 'success', 'message': 'Event stored successfully'}), 200
            else:
                logger.error("Failed to store event in database")
                return jsonify({'error': 'Failed to store event'}), 500
        else:
            logger.info(f"Event ignored - not processed: {event_type}")
            return jsonify({'status': 'ignored', 'message': 'Event not processed'}), 200
            
    except Exception as e:
        logger.error(f"Webhook error: {e}", exc_info=True)
        return jsonify({'error': 'Internal server error'}), 500

@webhook.route('/api/events')
@log_request_info
def get_events():
    """API endpoint to get latest events"""
    try:
        logger.info("Fetching events from database...")
        events = db.get_latest_events()
        
        if events:
            logger.info(f"Successfully retrieved {len(events)} events from database")
        else:
            logger.info("No events found in database")
        
        return jsonify(events)
    except Exception as e:
        logger.error(f"API error while fetching events: {e}", exc_info=True)
        return jsonify({'error': 'Failed to fetch events'}), 500