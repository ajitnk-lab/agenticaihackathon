import json
import boto3
import requests
import os
import time
import random
from botocore.exceptions import ClientError

def lambda_handler(event, context):
    """Lambda function to orchestrate Bedrock Agent calls to AgentCore runtimes"""
    
    try:
        # Parse Bedrock Agent event
        action_group = event.get('actionGroup', '')
        api_path = event.get('apiPath', '')
        http_method = event.get('httpMethod', 'POST')
        request_body = event.get('requestBody', {})
        
        # Get AgentCore endpoints from environment
        security_endpoint = os.getenv('SECURITY_AGENTCORE_ENDPOINT')
        cost_endpoint = os.getenv('COST_AGENTCORE_ENDPOINT')
        
        # Route to appropriate AgentCore runtime
        if api_path == '/analyze-security':
            result = call_agentcore(security_endpoint, "analyze_security_posture", request_body)
        elif api_path == '/calculate-roi':
            result = call_agentcore(cost_endpoint, "calculate_security_roi", request_body)
        elif api_path == '/get-trends':
            result = call_agentcore(cost_endpoint, "get_roi_trends", request_body)
        else:
            result = {"error": f"Unknown API path: {api_path}"}
        
        # Return Bedrock Agent response format
        return {
            'messageVersion': '1.0',
            'response': {
                'actionGroup': action_group,
                'apiPath': api_path,
                'httpMethod': http_method,
                'httpStatusCode': 200,
                'responseBody': {
                    'application/json': {
                        'body': json.dumps(result)
                    }
                }
            }
        }
        
    except Exception as e:
        return {
            'messageVersion': '1.0',
            'response': {
                'actionGroup': action_group,
                'apiPath': api_path,
                'httpMethod': http_method,
                'httpStatusCode': 500,
                'responseBody': {
                    'application/json': {
                        'body': json.dumps({"error": str(e)})
                    }
                }
            }
        }

def call_agentcore(endpoint, tool_name, request_body):
    """Call AgentCore runtime with specified tool and retry logic"""
    
    if not endpoint:
        # Fallback to local testing
        return test_agentcore_locally(tool_name, request_body)
    
    max_retries = 3
    base_delay = 1
    
    for attempt in range(max_retries):
        try:
            payload = {
                "prompt": tool_name,
                "parameters": request_body
            }
            
            response = requests.post(endpoint, json=payload, timeout=30)
            response.raise_for_status()
            
            return response.json()
            
        except requests.exceptions.RequestException as e:
            if attempt < max_retries - 1:
                # Exponential backoff with jitter
                delay = base_delay * (2 ** attempt) + random.uniform(0, 1)
                time.sleep(delay)
                continue
            return {"error": f"AgentCore call failed after {max_retries} attempts: {str(e)}"}
        except Exception as e:
            return {"error": f"AgentCore call failed: {str(e)}"}

def test_agentcore_locally(tool_name, request_body):
    """Local testing fallback when AgentCore endpoints not available"""
    
    if tool_name == "analyze_security_posture":
        return {
            "account_id": request_body.get("account_id", "123456789012"),
            "security_score": 85,
            "compliance_rate": 78,
            "recommendations": ["Enable GuardDuty", "Configure Security Hub"]
        }
    elif tool_name == "calculate_security_roi":
        return {
            "account_id": request_body.get("account_id", "123456789012"),
            "roi_percentage": 250.0,
            "annual_investment": 15009.0,
            "potential_savings": 52531.5
        }
    elif tool_name == "get_roi_trends":
        return {
            "trend": "improving",
            "data_points": 3
        }
    else:
        return {"error": f"Unknown tool: {tool_name}"}
