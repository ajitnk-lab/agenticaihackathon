#!/usr/bin/env python3
"""
Security Orchestrator Lambda Function - Working Version
Handles Bedrock Agent action groups and returns mock data from AgentCore
"""

import json
import boto3
import logging
import uuid

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def handle_security_analysis(parameters: dict) -> dict:
    """Handle security posture analysis"""
    account_id = parameters.get('account_id', '039920874011')
    
    try:
        # Return data that matches our AgentCore security agent output
        result = {
            "account_id": account_id,
            "region": "us-east-1",
            "security_score": 75,
            "critical_findings": 3,
            "high_findings": 8,
            "medium_findings": 15,
            "low_findings": 22,
            "recommendations": [
                "Enable GuardDuty in all regions",
                "Configure Security Hub standards", 
                "Enable CloudTrail logging",
                "Review IAM policies for least privilege",
                "Enable VPC Flow Logs"
            ],
            "compliance_status": "PARTIAL_COMPLIANCE",
            "services_analyzed": [
                "Amazon GuardDuty",
                "AWS Security Hub", 
                "Amazon Inspector",
                "AWS Config"
            ]
        }
        
        return {
            'statusCode': 200,
            'body': result
        }
    except Exception as e:
        logger.error(f"Error in security analysis: {str(e)}")
        return {
            'statusCode': 500,
            'body': {'error': str(e)}
        }

def handle_cost_analysis(parameters: dict) -> dict:
    """Handle security cost analysis"""
    account_id = parameters.get('account_id', '039920874011')
    days = parameters.get('days', 30)
    
    try:
        # Return data that matches our AgentCore cost agent output
        result = {
            'account_id': account_id,
            'period_days': days,
            'total_security_cost': 97.15,
            'service_costs': {
                'Amazon GuardDuty': 45.50,
                'AWS Security Hub': 12.30,
                'Amazon Inspector': 8.75,
                'AWS Config': 25.40,
                'AWS CloudTrail': 5.20
            },
            'currency': 'USD'
        }
        
        return {
            'statusCode': 200,
            'body': result
        }
    except Exception as e:
        logger.error(f"Error in cost analysis: {str(e)}")
        return {
            'statusCode': 500,
            'body': {'error': str(e)}
        }

def handle_roi_calculation(parameters: dict) -> dict:
    """Handle ROI calculation"""
    try:
        result = {
            'total_annual_investment': 2000.0,
            'total_potential_savings': 75000.0,
            'net_annual_benefit': 73000.0,
            'roi_percentage': 3650.0,
            'currency': 'USD'
        }
        
        return {
            'statusCode': 200,
            'body': result
        }
    except Exception as e:
        logger.error(f"Error calculating ROI: {str(e)}")
        return {
            'statusCode': 500,
            'body': {'error': str(e)}
        }

def lambda_handler(event, context):
    """Main Lambda handler for Bedrock Agent action groups"""
    try:
        logger.info(f"Received event: {json.dumps(event)}")
        
        # Extract Bedrock Agent parameters
        action_group = event.get('actionGroup', '')
        api_path = event.get('apiPath', '')
        http_method = event.get('httpMethod', 'POST')
        parameters = {}
        
        # Parse parameters from event
        if 'parameters' in event:
            for param in event['parameters']:
                parameters[param['name']] = param['value']
        
        # Route to appropriate handler
        if 'security' in api_path.lower() or 'analyze' in api_path.lower():
            result = handle_security_analysis(parameters)
        elif 'cost' in api_path.lower():
            result = handle_cost_analysis(parameters)
        elif 'roi' in api_path.lower():
            result = handle_roi_calculation(parameters)
        else:
            # Default to security analysis
            result = handle_security_analysis(parameters)
        
        # Format response for Bedrock Agent
        response = {
            'messageVersion': '1.0',
            'response': {
                'actionGroup': action_group,
                'apiPath': api_path,
                'httpMethod': http_method,
                'httpStatusCode': result.get('statusCode', 200),
                'responseBody': {
                    'application/json': {
                        'body': json.dumps(result.get('body', {}))
                    }
                }
            }
        }
        
        logger.info(f"Returning response: {json.dumps(response)}")
        return response
        
    except Exception as e:
        logger.error(f"Error in lambda_handler: {str(e)}")
        return {
            'messageVersion': '1.0',
            'response': {
                'actionGroup': event.get('actionGroup', ''),
                'apiPath': event.get('apiPath', ''),
                'httpMethod': event.get('httpMethod', 'POST'),
                'httpStatusCode': 500,
                'responseBody': {
                    'application/json': {
                        'body': json.dumps({'error': str(e)})
                    }
                }
            }
        }
