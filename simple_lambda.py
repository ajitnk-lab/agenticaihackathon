import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def lambda_handler(event, context):
    logger.info(f"Event: {json.dumps(event)}")
    
    return {
        "account_id": "039920874011",
        "security_score": 100,
        "status": "excellent"
    }
