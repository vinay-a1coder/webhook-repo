from flask import request
from ..extensions import WebhookDB
from datetime import datetime, timezone
import logging
from dateutil import parser

db = WebhookDB()

logger = logging.getLogger(__name__)

def parse_timestamp(timestamp_str, fallback_message="No timestamp found"):
    """
    Parse timestamp string to datetime object with UTC conversion
    """
    if timestamp_str:
        try:
            # Parse the timestamp string
            timestamp = parser.parse(timestamp_str)
            
            # Always convert to UTC and make timezone-naive for consistency
            if timestamp.tzinfo is not None:
                # If it has timezone info, convert to UTC
                timestamp_utc = timestamp.astimezone(timezone.utc)
            else:
                # If no timezone info, assume it's already UTC
                timestamp_utc = timestamp.replace(tzinfo=timezone.utc)
            
            # Make it timezone-naive (remove timezone info but keep UTC time)
            timestamp_final = timestamp_utc.replace(tzinfo=None)
            
            logger.debug(f"Parsed timestamp: {timestamp_str} -> {timestamp_final}")
            return timestamp_final
            
        except Exception as e:
            logger.warning(f"Failed to parse timestamp '{timestamp_str}': {e}, using current UTC time")
            return datetime.utcnow()
    else:
        logger.debug(f"{fallback_message}, using current UTC time")
        return datetime.utcnow()
    
def parse_webhook_data(payload):
    """Parse GitHub webhook payload and extract relevant information"""
    try:
        event_type = request.headers.get('X-GitHub-Event', 'unknown')
        logger.info(f"Processing webhook event: {event_type}")
        
        if event_type == 'push':
            logger.debug("Parsing push event")
            return parse_push_event(payload)
        elif event_type == 'pull_request':
            logger.debug("Parsing pull request event")
            return parse_pull_request_event(payload)
        else:
            logger.warning(f"Unsupported event type: {event_type}")
            return None
    except Exception as e:
        logger.error(f"Error parsing webhook data: {e}", exc_info=True)
        return None
    
def parse_push_event(payload):
    """Parse push event data"""
    try:
        author = payload.get('head_commit', {}).get('author', {}).get('name', 'Unknown')
        branch = payload.get('ref', '').replace('refs/heads/', '')
        timestamp_str = payload.get('head_commit', {}).get('timestamp')

        timestamp = parse_timestamp(timestamp_str, "No timestamp found in push event")
        
        result = {
            'action': 'push',
            'author': author,
            'to_branch': branch,
            'from_branch': None,
            'timestamp': timestamp
        }

        logger.info(f"Successfully parsed push event: author={author}, branch={branch}")
        logger.debug(f"Push event details: {result}")
        return result
    
    except Exception as e:
        logger.error(f"Error parsing push event: {e}", exc_info=True)
        return None

def parse_pull_request_event(payload):
    """Parse pull request event data"""
    try:
        pr_action = payload.get('action', '')
        logger.debug(f"Pull request action: {pr_action}")
        
        if pr_action == 'opened':
            author = payload.get('pull_request', {}).get('user', {}).get('login', 'Unknown')
            from_branch = payload.get('pull_request', {}).get('head', {}).get('ref', 'Unknown')
            to_branch = payload.get('pull_request', {}).get('base', {}).get('ref', 'Unknown')
            timestamp_str = payload.get('pull_request', {}).get('created_at')

            timestamp = parse_timestamp(timestamp_str, "No timestamp found in PR opened event")
            
            result = {
                'action': 'pull_request',
                'author': author,
                'from_branch': from_branch,
                'to_branch': to_branch,
                'timestamp': timestamp
            }

            logger.info(f"Successfully parsed PR opened event: author={author}, {from_branch} -> {to_branch}")
            logger.debug(f"PR opened event details: {result}")
            return result
        
        elif pr_action == 'closed' and payload.get('pull_request', {}).get('merged', False):
            author = payload.get('pull_request', {}).get('user', {}).get('login', 'Unknown')
            from_branch = payload.get('pull_request', {}).get('head', {}).get('ref', 'Unknown')
            to_branch = payload.get('pull_request', {}).get('base', {}).get('ref', 'Unknown')
            timestamp_str = payload.get('pull_request', {}).get('merged_at')
            
            timestamp = parse_timestamp(timestamp_str, "No timestamp found in PR merge event")
            
            result = {
                'action': 'merge',
                'author': author,
                'from_branch': from_branch,
                'to_branch': to_branch,
                'timestamp': timestamp
            }

            logger.info(f"Successfully parsed PR merge event: author={author}, {from_branch} -> {to_branch}")
            logger.debug(f"PR merge event details: {result}")
            return result
        
        else:
            logger.debug(f"Skipping PR event - action: {pr_action}, merged: {payload.get('pull_request', {}).get('merged', False)}")
            return None
        
    except Exception as e:
        logger.error(f"Error parsing pull request event: {e}", exc_info=True)
        return None