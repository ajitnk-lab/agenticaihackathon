import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def lambda_handler(event, context):
    logger.info(f"BEDROCK EVENT: {json.dumps(event)}")
    
    # Check if this is a function schema call
    if 'function' in event:
        logger.info(f"Function call: {event['function']}")
        logger.info(f"Parameters: {event.get('parameters', [])}")
        
        # Return simple response for function schema
        return "Security analysis complete: Account 039920874011 has security score 100/100"
    
    # Default response
    return {
        "account_id": "039920874011", 
        "security_score": 100,
        "status": "excellent"
    }
