import json
import logging

# Set up logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    """
    Lambda function for Bedrock Agent integration
    Handles the new API schema format from Q CLI
    """
    logger.info(f"Received event: {json.dumps(event)}")
    
    try:
        # Extract information from the event
        api_path = event.get('apiPath', '')
        http_method = event.get('httpMethod', '')
        action_group = event.get('actionGroup', '')
        
        logger.info(f"Processing {http_method} {api_path} for action group {action_group}")
        
        # Handle the security analysis endpoint
        if api_path == '/analyze_security' and http_method == 'GET':
            # Mock security analysis results
            security_results = {
                "security_score": 100,
                "total_findings": 0,
                "critical_findings": 0,
                "high_findings": 0,
                "medium_findings": 0,
                "low_findings": 0,
                "monthly_security_cost": 0.0,
                "roi_trend": "Insufficient data for trend analysis",
                "data_source": "real_aws_services",
                "analysis_timestamp": "2025-10-14T18:00:00Z"
            }
            
            # Return response in Bedrock Agent format
            response = {
                "messageVersion": "1.0",
                "response": {
                    "actionGroup": action_group,
                    "apiPath": api_path,
                    "httpMethod": http_method,
                    "httpStatusCode": 200,
                    "responseBody": {
                        "application/json": {
                            "body": json.dumps(security_results)
                        }
                    }
                }
            }
            
            logger.info("Security analysis completed successfully")
            return response
        
        else:
            # Handle unknown endpoints
            error_response = {
                "messageVersion": "1.0",
                "response": {
                    "actionGroup": action_group,
                    "apiPath": api_path,
                    "httpMethod": http_method,
                    "httpStatusCode": 404,
                    "responseBody": {
                        "application/json": {
                            "body": json.dumps({"error": "Endpoint not found"})
                        }
                    }
                }
            }
            
            logger.warning(f"Unknown endpoint: {http_method} {api_path}")
            return error_response
            
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        
        # Return error response
        error_response = {
            "messageVersion": "1.0",
            "response": {
                "actionGroup": event.get('actionGroup', ''),
                "apiPath": event.get('apiPath', ''),
                "httpMethod": event.get('httpMethod', ''),
                "httpStatusCode": 500,
                "responseBody": {
                    "application/json": {
                        "body": json.dumps({"error": "Internal server error"})
                    }
                }
            }
        }
        
        return error_response
