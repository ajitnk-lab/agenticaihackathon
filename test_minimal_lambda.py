#!/usr/bin/env python3
"""Minimal Lambda function for testing Bedrock Agent"""

import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def lambda_handler(event, context):
    """Minimal handler for testing"""
    try:
        logger.info(f"Received event: {json.dumps(event)}")
        
        # Return minimal response
        response = {
            "message": "Security analysis complete",
            "account_id": "039920874011",
            "security_score": 100
        }
        
        logger.info(f"Returning: {json.dumps(response)}")
        return response
        
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return {"error": str(e)}
