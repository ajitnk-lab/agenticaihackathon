import json
import logging
import requests
import os

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    """
    Lambda function that calls AgentCore agents via HTTP
    """
    logger.info(f"Received event: {json.dumps(event)}")
    
    try:
        api_path = event.get('apiPath', '')
        http_method = event.get('httpMethod', '')
        action_group = event.get('actionGroup', '')
        
        if api_path == '/analyze_security' and http_method == 'GET':
            # Call AgentCore agents
            security_results = call_agentcore_agents()
            
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
            
            return response
        
        else:
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
            return error_response
            
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return {
            "messageVersion": "1.0",
            "response": {
                "actionGroup": event.get('actionGroup', ''),
                "apiPath": event.get('apiPath', ''),
                "httpMethod": event.get('httpMethod', ''),
                "httpStatusCode": 500,
                "responseBody": {
                    "application/json": {
                        "body": json.dumps({"error": str(e)})
                    }
                }
            }
        }

def call_agentcore_agents():
    """Call the deployed AgentCore agents"""
    try:
        # Get AgentCore endpoints from environment or use defaults
        security_endpoint = os.environ.get('SECURITY_AGENTCORE_URL', 'https://your-security-agent.agentcore.aws')
        cost_endpoint = os.environ.get('COST_AGENTCORE_URL', 'https://your-cost-agent.agentcore.aws')
        
        # Call security analysis agent
        security_response = requests.post(
            f"{security_endpoint}/analyze",
            json={"action": "analyze_security"},
            timeout=30
        )
        
        # Call cost analysis agent  
        cost_response = requests.post(
            f"{cost_endpoint}/analyze", 
            json={"action": "analyze_costs"},
            timeout=30
        )
        
        # Combine results
        results = {
            "security_analysis": security_response.json() if security_response.status_code == 200 else {"error": "Security analysis failed"},
            "cost_analysis": cost_response.json() if cost_response.status_code == 200 else {"error": "Cost analysis failed"},
            "timestamp": "2025-10-14T18:25:00Z"
        }
        
        return results
        
    except Exception as e:
        logger.error(f"Error calling AgentCore agents: {str(e)}")
        # Fallback to mock data if AgentCore not available
        return {
            "security_score": 100,
            "total_findings": 0,
            "monthly_security_cost": 0.0,
            "roi_trend": "AgentCore agents not available - using fallback data",
            "error": str(e)
        }
