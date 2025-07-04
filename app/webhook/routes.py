from flask import Blueprint, json, request, jsonify, render_template
from .utils import parse_webhook_data, db

webhook = Blueprint('Webhook', __name__)

@webhook.route('/receiver', methods=["POST"])
def receiver():
    return {}, 200


@webhook.route('/')
def index():
    """Main page displaying GitHub events"""
    return render_template('index.html')

@webhook.route('/webhook', methods=['POST'])
def webhooks():
    """Webhook endpoint to receive GitHub events"""
    try:
        payload = request.get_json()
        
        if not payload:
            return jsonify({'error': 'No payload received'}), 400
        
        # Parse the webhook data
        event_data = parse_webhook_data(payload)
        
        if event_data:
            # Store in database
            result = db.insert_event(event_data)
            if result:
                return jsonify({'status': 'success', 'message': 'Event stored successfully'}), 200
            else:
                return jsonify({'error': 'Failed to store event'}), 500
        else:
            return jsonify({'status': 'ignored', 'message': 'Event not processed'}), 200
            
    except Exception as e:
        print(f"Webhook error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@webhook.route('/api/events')
def get_events():
    """API endpoint to get latest events"""
    try:
        events = db.get_latest_events()
        # Convert ObjectId to string for JSON serialization
        for event in events:
            event['_id'] = str(event['_id'])
        return jsonify(events)
    except Exception as e:
        print(f"API error: {e}")
        return jsonify({'error': 'Failed to fetch events'}), 500