#!/usr/bin/env python3
"""Quick deployment script to restore development capability"""

import boto3
import zipfile
import os
import json

def deploy_agentcore_backend():
    """Deploy the AgentCore Memory backend"""
    lambda_client = boto3.client('lambda', region_name='us-east-1')
    
    # Create zip file
    with zipfile.ZipFile('agentcore_backend.zip', 'w') as z:
        z.write('agentcore_memory_backend_fixed.py', 'lambda_function.py')
    
    # Update function
    with open('agentcore_backend.zip', 'rb') as f:
        lambda_client.update_function_code(
            FunctionName='agentcore-memory-backend',
            ZipFile=f.read()
        )
    
    print("✅ AgentCore Memory backend deployed")

def deploy_dashboard():
    """Deploy the dashboard"""
    lambda_client = boto3.client('lambda', region_name='us-east-1')
    
    # Create zip file
    with zipfile.ZipFile('dashboard.zip', 'w') as z:
        z.write('dashboard_memory_trends.html', 'dashboard.html')
        
        # Create simple lambda handler
        handler_code = '''
import json

def lambda_handler(event, context):
    with open('dashboard.html', 'r') as f:
        html = f.read()
    
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'text/html',
            'Access-Control-Allow-Origin': '*'
        },
        'body': html
    }
'''
        z.writestr('lambda_function.py', handler_code)
    
    # Update function
    with open('dashboard.zip', 'rb') as f:
        lambda_client.update_function_code(
            FunctionName='security-roi-dashboard',
            ZipFile=f.read()
        )
    
    print("✅ Dashboard deployed")

if __name__ == "__main__":
    print("🚀 Quick deployment starting...")
    deploy_agentcore_backend()
    deploy_dashboard()
    print("✅ Deployment complete!")
    print("Dashboard: https://tajuooav2jms35ubhnhtiscqvy0usgih.lambda-url.us-east-1.on.aws/")
    print("Backend: https://vxlk4vnqccr5jp7p4aln34wdge0xaudq.lambda-url.us-east-1.on.aws/")
