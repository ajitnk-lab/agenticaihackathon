#!/usr/bin/env python3
"""Deploy Lambda function for Bedrock Agent integration"""

import boto3
import zipfile
import os
import json

def create_lambda_package():
    """Create deployment package for Lambda"""
    
    # Create zip file
    with zipfile.ZipFile('security-roi-lambda.zip', 'w') as zip_file:
        # Add Lambda function
        zip_file.write('src/lambda/bedrock_agent_lambda.py', 'lambda_function.py')
    
    print("✅ Lambda package created: security-roi-lambda.zip")
    return 'security-roi-lambda.zip'

def deploy_lambda_function():
    """Deploy Lambda function to AWS"""
    
    lambda_client = boto3.client('lambda')
    
    # Create deployment package
    package_path = create_lambda_package()
    
    try:
        # Read zip file
        with open(package_path, 'rb') as zip_file:
            zip_content = zip_file.read()
        
        # Create or update Lambda function
        function_name = 'security-roi-orchestrator'
        
        try:
            # Try to update existing function
            response = lambda_client.update_function_code(
                FunctionName=function_name,
                ZipFile=zip_content
            )
            print(f"✅ Updated Lambda function: {function_name}")
            
        except lambda_client.exceptions.ResourceNotFoundException:
            # Create new function
            response = lambda_client.create_function(
                FunctionName=function_name,
                Runtime='python3.9',
                Role='arn:aws:iam::123456789012:role/SecurityROILambdaRole',  # Update with actual role
                Handler='lambda_function.lambda_handler',
                Code={'ZipFile': zip_content},
                Description='Security ROI Calculator - Bedrock Agent orchestrator',
                Timeout=30,
                Environment={
                    'Variables': {
                        'SECURITY_AGENTCORE_ENDPOINT': '',
                        'COST_AGENTCORE_ENDPOINT': ''
                    }
                }
            )
            print(f"✅ Created Lambda function: {function_name}")
        
        print(f"Function ARN: {response['FunctionArn']}")
        return response['FunctionArn']
        
    except Exception as e:
        print(f"❌ Lambda deployment failed: {e}")
        return None
    
    finally:
        # Clean up
        if os.path.exists(package_path):
            os.remove(package_path)

def test_lambda_function():
    """Test Lambda function locally"""
    
    print("\n🧪 Testing Lambda function locally...")
    
    # Import Lambda function
    import sys
    sys.path.append('src/lambda')
    from bedrock_agent_lambda import lambda_handler
    
    # Test security analysis
    test_event = {
        'actionGroup': 'security-analysis',
        'apiPath': '/analyze-security',
        'httpMethod': 'POST',
        'requestBody': {'account_id': '123456789012'}
    }
    
    result = lambda_handler(test_event, {})
    response_body = json.loads(result['response']['responseBody']['application/json']['body'])
    
    print(f"✅ Security analysis test: Score = {response_body.get('security_score', 'N/A')}")
    
    # Test ROI calculation
    test_event['apiPath'] = '/calculate-roi'
    result = lambda_handler(test_event, {})
    response_body = json.loads(result['response']['responseBody']['application/json']['body'])
    
    print(f"✅ ROI calculation test: ROI = {response_body.get('roi_percentage', 'N/A')}%")

if __name__ == "__main__":
    print("🚀 Deploying Security ROI Lambda Function...")
    
    # Test locally first
    test_lambda_function()
    
    # Deploy to AWS (commented out for safety)
    # function_arn = deploy_lambda_function()
    print("\n💡 To deploy to AWS, uncomment the deploy_lambda_function() call")
    print("💡 Make sure to update the IAM role ARN in the script first")
