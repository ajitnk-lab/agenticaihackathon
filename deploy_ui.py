#!/usr/bin/env python3
"""
Deploy UI to AWS - S3 + CloudFront + Lambda
"""

import boto3
import json
import zipfile
import os
from datetime import datetime

def create_s3_bucket():
    """Create S3 bucket for static files"""
    s3 = boto3.client('s3')
    bucket_name = f"security-dashboard-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    try:
        s3.create_bucket(Bucket=bucket_name)
        print(f"✅ Created S3 bucket: {bucket_name}")
        return bucket_name
    except Exception as e:
        print(f"❌ S3 bucket creation failed: {e}")
        return None

def upload_static_files(bucket_name):
    """Upload HTML/JS/CSS to S3"""
    s3 = boto3.client('s3')
    
    files = [
        ('dashboard.html', 'text/html'),
        ('dashboard.js', 'application/javascript')
    ]
    
    for filename, content_type in files:
        if os.path.exists(filename):
            s3.upload_file(
                filename, bucket_name, filename,
                ExtraArgs={'ContentType': content_type}
            )
            print(f"✅ Uploaded {filename}")

def create_lambda_function():
    """Create Lambda function for API"""
    lambda_client = boto3.client('lambda')
    
    # Create deployment package
    with zipfile.ZipFile('dashboard_lambda.zip', 'w') as z:
        z.write('dashboard_api.py', 'lambda_function.py')
    
    with open('dashboard_lambda.zip', 'rb') as f:
        zip_content = f.read()
    
    try:
        response = lambda_client.create_function(
            FunctionName='security-dashboard-api',
            Runtime='python3.9',
            Role='arn:aws:iam::039920874011:role/lambda-execution-role',
            Handler='lambda_function.lambda_handler',
            Code={'ZipFile': zip_content},
            Environment={
                'Variables': {
                    'AGENTCORE_PATH': '/tmp'
                }
            }
        )
        print(f"✅ Created Lambda: {response['FunctionArn']}")
        return response['FunctionArn']
    except Exception as e:
        print(f"❌ Lambda creation failed: {e}")
        return None

def create_api_gateway(lambda_arn):
    """Create API Gateway"""
    api = boto3.client('apigateway')
    
    try:
        # Create REST API
        response = api.create_rest_api(
            name='security-dashboard-api',
            description='Security Dashboard API'
        )
        api_id = response['id']
        
        # Get root resource
        resources = api.get_resources(restApiId=api_id)
        root_id = resources['items'][0]['id']
        
        # Create /api resource
        api_resource = api.create_resource(
            restApiId=api_id,
            parentId=root_id,
            pathPart='api'
        )
        
        # Create method
        api.put_method(
            restApiId=api_id,
            resourceId=api_resource['id'],
            httpMethod='GET',
            authorizationType='NONE'
        )
        
        # Create integration
        api.put_integration(
            restApiId=api_id,
            resourceId=api_resource['id'],
            httpMethod='GET',
            type='AWS_PROXY',
            integrationHttpMethod='POST',
            uri=f"arn:aws:apigateway:us-east-1:lambda:path/2015-03-31/functions/{lambda_arn}/invocations"
        )
        
        # Deploy API
        api.create_deployment(
            restApiId=api_id,
            stageName='prod'
        )
        
        api_url = f"https://{api_id}.execute-api.us-east-1.amazonaws.com/prod"
        print(f"✅ Created API Gateway: {api_url}")
        return api_url
        
    except Exception as e:
        print(f"❌ API Gateway creation failed: {e}")
        return None

def main():
    print("🚀 Deploying Security Dashboard to AWS...")
    
    # Create S3 bucket
    bucket_name = create_s3_bucket()
    if not bucket_name:
        return
    
    # Upload static files
    upload_static_files(bucket_name)
    
    # Create Lambda
    lambda_arn = create_lambda_function()
    if not lambda_arn:
        return
    
    # Create API Gateway
    api_url = create_api_gateway(lambda_arn)
    
    # Output URLs
    s3_url = f"https://{bucket_name}.s3.amazonaws.com/dashboard.html"
    
    print("\n🎉 Deployment Complete!")
    print(f"📊 Dashboard URL: {s3_url}")
    print(f"🔗 API URL: {api_url}")

if __name__ == "__main__":
    main()
