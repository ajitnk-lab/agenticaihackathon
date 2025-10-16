#!/usr/bin/env python3
"""
Deploy Bedrock Agent Orchestrated Chatbot
"""

import boto3
import json
import zipfile
import os
from datetime import datetime

def deploy_bedrock_orchestrated_chatbot():
    """Deploy the properly orchestrated chatbot"""
    
    lambda_client = boto3.client('lambda', region_name='us-east-1')
    
    # Create deployment package
    zip_path = create_deployment_package()
    
    function_name = 'bedrock-agent-orchestrated-chatbot'
    
    try:
        # Check if function exists
        try:
            lambda_client.get_function(FunctionName=function_name)
            print(f"Updating existing function: {function_name}")
            
            # Update function code
            with open(zip_path, 'rb') as zip_file:
                lambda_client.update_function_code(
                    FunctionName=function_name,
                    ZipFile=zip_file.read()
                )
            
        except lambda_client.exceptions.ResourceNotFoundException:
            print(f"Creating new function: {function_name}")
            
            # Create new function
            with open(zip_path, 'rb') as zip_file:
                response = lambda_client.create_function(
                    FunctionName=function_name,
                    Runtime='python3.9',
                    Role='arn:aws:iam::039920874011:role/lambda-execution-role',
                    Handler='bedrock_orchestrated_chatbot.lambda_handler',
                    Code={'ZipFile': zip_file.read()},
                    Description='Bedrock Agent Orchestrated Security Chatbot',
                    Timeout=60,
                    MemorySize=512,
                    Environment={
                        'Variables': {
                            'BEDROCK_AGENT_ID': 'QDVHR8CMIW',
                            'BEDROCK_AGENT_ALIAS': 'TSTALIASID'
                        }
                    }
                )
        
        # Create or update Function URL
        try:
            url_response = lambda_client.create_function_url_config(
                FunctionName=function_name,
                AuthType='NONE',
                Cors={
                    'AllowCredentials': False,
                    'AllowHeaders': ['*'],
                    'AllowMethods': ['*'],
                    'AllowOrigins': ['*'],
                    'MaxAge': 86400
                }
            )
            function_url = url_response['FunctionUrl']
            
        except lambda_client.exceptions.ResourceConflictException:
            # URL already exists, get it
            url_response = lambda_client.get_function_url_config(FunctionName=function_name)
            function_url = url_response['FunctionUrl']
        
        print(f"\n✅ Deployment successful!")
        print(f"🔗 Chatbot URL: {function_url}")
        print(f"🤖 Bedrock Agent: QDVHR8CMIW (SecurityROICalculatorUpdated)")
        print(f"🎯 Architecture: UI → Bedrock Agent → AgentCore Agents → AWS APIs")
        
        return function_url
        
    except Exception as e:
        print(f"❌ Deployment failed: {str(e)}")
        return None
    
    finally:
        # Clean up
        if os.path.exists(zip_path):
            os.remove(zip_path)

def create_deployment_package():
    """Create deployment package"""
    
    zip_path = '/tmp/bedrock_orchestrated_chatbot.zip'
    
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        # Add the main chatbot file
        zip_file.write(
            '/persistent/home/ubuntu/workspace/agenticaihackathon/bedrock_agent_chatbot/bedrock_orchestrated_chatbot.py',
            'bedrock_orchestrated_chatbot.py'
        )
    
    return zip_path

if __name__ == '__main__':
    deploy_bedrock_orchestrated_chatbot()
