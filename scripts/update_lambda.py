#!/usr/bin/env python3
"""Deploy updated Lambda function that calls AgentCore runtimes"""

import boto3
import zipfile
import os
from pathlib import Path

lambda_client = boto3.client('lambda', region_name='us-east-1')

FUNCTION_NAME = "security-orchestrator-bedrock-agent"
LAMBDA_FILE = "/persistent/home/ubuntu/workspace/agenticaihackathon/src/lambda/lambda_function.py"
ZIP_FILE = "/tmp/lambda_deployment.zip"

def create_deployment_package():
    """Create Lambda deployment package"""
    print("📦 Creating deployment package...")
    
    with zipfile.ZipFile(ZIP_FILE, 'w', zipfile.ZIP_DEFLATED) as zipf:
        zipf.write(LAMBDA_FILE, 'lambda_function.py')
    
    print(f"✅ Package created: {ZIP_FILE}")
    return ZIP_FILE

def update_lambda_code():
    """Update Lambda function code"""
    print(f"🚀 Updating Lambda function: {FUNCTION_NAME}")
    
    with open(ZIP_FILE, 'rb') as f:
        zip_content = f.read()
    
    response = lambda_client.update_function_code(
        FunctionName=FUNCTION_NAME,
        ZipFile=zip_content
    )
    
    print(f"✅ Lambda updated: {response['FunctionArn']}")
    print(f"   Version: {response['Version']}")
    print(f"   Last Modified: {response['LastModified']}")
    
    return response

def verify_environment():
    """Verify AgentCore ARNs are configured"""
    print("\n🔍 Verifying environment variables...")
    
    config = lambda_client.get_function_configuration(FunctionName=FUNCTION_NAME)
    env_vars = config.get('Environment', {}).get('Variables', {})
    
    security_arn = env_vars.get('SECURITY_AGENT_ARN', 'NOT_SET')
    cost_arn = env_vars.get('COST_AGENT_ARN', 'NOT_SET')
    
    print(f"   SECURITY_AGENT_ARN: {security_arn}")
    print(f"   COST_AGENT_ARN: {cost_arn}")
    
    if 'NOT_SET' in [security_arn, cost_arn]:
        print("⚠️  Warning: AgentCore ARNs not configured!")
        return False
    
    print("✅ Environment variables configured correctly")
    return True

if __name__ == "__main__":
    print("🔧 Lambda Deployment Script")
    print("="*60)
    
    # Create package
    create_deployment_package()
    
    # Update Lambda
    update_lambda_code()
    
    # Verify environment
    verify_environment()
    
    print("\n✅ Deployment complete!")
    print("Test with: python3 tests/test_complete_flow.py")
