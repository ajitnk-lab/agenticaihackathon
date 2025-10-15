import json
import subprocess
import os

def lambda_handler(event, context):
    """Lambda handler for dashboard API"""
    
    # CORS headers
    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Access-Control-Allow-Methods': 'GET, POST, OPTIONS'
    }
    
    try:
        # Handle OPTIONS request
        if event.get('httpMethod') == 'OPTIONS':
            return {
                'statusCode': 200,
                'headers': headers,
                'body': ''
            }
        
        # Get query parameters
        query_params = event.get('queryStringParameters', {}) or {}
        action = query_params.get('action', 'security')
        
        # Mock AgentCore response (since AgentCore CLI not available in Lambda)
        if action == 'security':
            response_data = {
                "security_score": 85,
                "findings": 151,
                "services": ["GuardDuty", "Inspector", "Security Hub", "Macie", "Access Analyzer"],
                "critical_findings": 12,
                "high_findings": 34,
                "medium_findings": 67,
                "low_findings": 38
            }
        elif action == 'cost':
            response_data = {
                "monthly_cost": 128,
                "roi_percentage": 23337,
                "cost_breakdown": {
                    "GuardDuty": 45,
                    "Inspector": 25,
                    "Security Hub": 15,
                    "Macie": 35,
                    "Access Analyzer": 8
                }
            }
        else:
            response_data = {"error": "Unknown action"}
        
        return {
            'statusCode': 200,
            'headers': headers,
            'body': json.dumps(response_data)
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': headers,
            'body': json.dumps({'error': str(e)})
        }
