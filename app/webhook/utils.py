from flask import request
from ..extensions import WebhookDB
from datetime import datetime

db = WebhookDB()

def parse_webhook_data(payload):
    """Parse GitHub webhook payload and extract relevant information"""
    try:
        event_type = request.headers.get('X-GitHub-Event', 'unknown')
        
        if event_type == 'push':
            return parse_push_event(payload)
        elif event_type == 'pull_request':
            return parse_pull_request_event(payload)
        else:
            return None
    except Exception as e:
        print(f"Error parsing webhook data: {e}")
        return None
    
def parse_push_event(payload):
    """Parse push event data"""
    try:
        author = payload.get('head_commit', {}).get('author', {}).get('name', 'Unknown')
        branch = payload.get('ref', '').replace('refs/heads/', '')
        timestamp = datetime.utcnow().isoformat()
        
        return {
            'action': 'push',
            'author': author,
            'to_branch': branch,
            'from_branch': None,
            'timestamp': timestamp,
            'message': f'"{author}" pushed to "{branch}" on {format_timestamp(timestamp)}'
        }
    except Exception as e:
        print(f"Error parsing push event: {e}")
        return None

def parse_pull_request_event(payload):
    """Parse pull request event data"""
    try:
        pr_action = payload.get('action', '')
        
        if pr_action == 'opened':
            author = payload.get('pull_request', {}).get('user', {}).get('login', 'Unknown')
            from_branch = payload.get('pull_request', {}).get('head', {}).get('ref', 'Unknown')
            to_branch = payload.get('pull_request', {}).get('base', {}).get('ref', 'Unknown')
            timestamp = datetime.utcnow().isoformat()
            
            return {
                'action': 'pull_request',
                'author': author,
                'from_branch': from_branch,
                'to_branch': to_branch,
                'timestamp': timestamp,
                'message': f'"{author}" submitted a pull request from "{from_branch}" to "{to_branch}" on {format_timestamp(timestamp)}'
            }
        elif pr_action == 'closed' and payload.get('pull_request', {}).get('merged', False):
            author = payload.get('pull_request', {}).get('user', {}).get('login', 'Unknown')
            from_branch = payload.get('pull_request', {}).get('head', {}).get('ref', 'Unknown')
            to_branch = payload.get('pull_request', {}).get('base', {}).get('ref', 'Unknown')
            timestamp = datetime.utcnow().isoformat()
            
            return {
                'action': 'merge',
                'author': author,
                'from_branch': from_branch,
                'to_branch': to_branch,
                'timestamp': timestamp,
                'message': f'"{author}" merged branch "{from_branch}" to "{to_branch}" on {format_timestamp(timestamp)}'
            }
    except Exception as e:
        print(f"Error parsing pull request event: {e}")
        return None

def format_timestamp(iso_timestamp):
    """Format timestamp for display"""
    try:
        dt = datetime.fromisoformat(iso_timestamp.replace('Z', '+00:00'))
        return dt.strftime('%d %B %Y - %I:%M %p UTC')
    except:
        return iso_timestamp