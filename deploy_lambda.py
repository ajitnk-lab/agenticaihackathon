#!/usr/bin/env python3
"""
Deploy Security Orchestrator Lambda Function
"""

import boto3
import zipfile
import json
import os

def create_lambda_function():
    """Create and deploy the Lambda function"""
    
    # Create deployment package
    with zipfile.ZipFile('security_orchestrator_lambda.zip', 'w') as zip_file:
        zip_file.write('security_orchestrator_lambda.py')
    
    # Read the zip file
    with open('security_orchestrator_lambda.zip', 'rb') as zip_file:
        zip_content = zip_file.read()
    
    lambda_client = boto3.client('lambda', region_name='us-east-1')
    iam_client = boto3.client('iam', region_name='us-east-1')
    
    # Create IAM role for Lambda
    trust_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {
                    "Service": "lambda.amazonaws.com"
                },
                "Action": "sts:AssumeRole"
            }
        ]
    }
    
    try:
        role_response = iam_client.create_role(
            RoleName='SecurityOrchestratorLambdaRole',
            AssumeRolePolicyDocument=json.dumps(trust_policy),
            Description='Role for Security Orchestrator Lambda function'
        )
        role_arn = role_response['Role']['Arn']
        print(f"Created IAM role: {role_arn}")
    except iam_client.exceptions.EntityAlreadyExistsException:
        role_response = iam_client.get_role(RoleName='SecurityOrchestratorLambdaRole')
        role_arn = role_response['Role']['Arn']
        print(f"Using existing IAM role: {role_arn}")
    
    # Attach policies
    policies = [
        'arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole',
        'arn:aws:iam::aws:policy/AmazonBedrockFullAccess'
    ]
    
    for policy in policies:
        try:
            iam_client.attach_role_policy(
                RoleName='SecurityOrchestratorLambdaRole',
                PolicyArn=policy
            )
            print(f"Attached policy: {policy}")
        except Exception as e:
            print(f"Policy already attached or error: {e}")
    
    # Wait for role to be ready
    import time
    time.sleep(10)
    
    # Create Lambda function
    try:
        response = lambda_client.create_function(
            FunctionName='security-orchestrator-bedrock-agent',
            Runtime='python3.10',
            Role=role_arn,
            Handler='security_orchestrator_lambda.lambda_handler',
            Code={'ZipFile': zip_content},
            Description='Security Orchestrator for Bedrock Agent',
            Timeout=300,
            MemorySize=512,
            Environment={
                'Variables': {
                    'SECURITY_AGENT_ARN': 'arn:aws:bedrock-agentcore:us-east-1:039920874011:runtime/well_architected_security_agentcore-uBgBoaAnRs',
                    'COST_AGENT_ARN': 'arn:aws:bedrock-agentcore:us-east-1:039920874011:runtime/cost_analysis_agentcore-UTdyrMH0Jo'
                }
            }
        )
        print(f"Created Lambda function: {response['FunctionArn']}")
        return response['FunctionArn']
        
    except lambda_client.exceptions.ResourceConflictException:
        # Update existing function
        response = lambda_client.update_function_code(
            FunctionName='security-orchestrator-bedrock-agent',
            ZipFile=zip_content
        )
        print(f"Updated Lambda function: {response['FunctionArn']}")
        return response['FunctionArn']

if __name__ == "__main__":
    function_arn = create_lambda_function()
    print(f"Lambda function ready: {function_arn}")
