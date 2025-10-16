#!/usr/bin/env python3
import json
import sys
import os
from datetime import datetime

# Add paths to import real AgentCore agents
sys.path.append('/opt/python/src')
sys.path.append('/var/task/src')
sys.path.append('/var/task')
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

def lambda_handler(event, context):
    """Handle requests using REAL AgentCore agents"""
    
    try:
        # Import real AgentCore agents
        from agentcore.well_architected_security_agentcore import analyze_security_posture
        from agentcore.cost_analysis_agentcore import get_updated_security_costs
        
        # Get real data from agents
        security_data = analyze_security_posture("039920874011")
        cost_data = get_updated_security_costs("039920874011")
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'security_data': security_data,
                'cost_data': cost_data,
                'timestamp': datetime.now().isoformat(),
                'data_source': 'real_agentcore_agents'
            })
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'error': str(e),
                'data_source': 'error'
            })
        }
