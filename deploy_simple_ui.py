#!/usr/bin/env python3
"""
Simple UI deployment to AWS
"""

import boto3
import json
import zipfile
import time

def deploy_lambda():
    """Deploy Lambda function"""
    lambda_client = boto3.client('lambda')
    
    # Create zip file
    with zipfile.ZipFile('dashboard_lambda.zip', 'w') as z:
        z.write('lambda_handler.py', 'lambda_function.py')
    
    with open('dashboard_lambda.zip', 'rb') as f:
        zip_content = f.read()
    
    try:
        # Delete existing function if it exists
        try:
            lambda_client.delete_function(FunctionName='security-dashboard-api')
            time.sleep(2)
        except:
            pass
        
        response = lambda_client.create_function(
            FunctionName='security-dashboard-api',
            Runtime='python3.9',
            Role='arn:aws:iam::039920874011:role/lambda-execution-role',
            Handler='lambda_function.lambda_handler',
            Code={'ZipFile': zip_content},
            Timeout=30
        )
        
        # Add API Gateway permission
        lambda_client.add_permission(
            FunctionName='security-dashboard-api',
            StatementId='api-gateway-invoke',
            Action='lambda:InvokeFunction',
            Principal='apigateway.amazonaws.com'
        )
        
        print(f"✅ Lambda deployed: {response['FunctionArn']}")
        return response['FunctionArn']
        
    except Exception as e:
        print(f"❌ Lambda deployment failed: {e}")
        return None

def deploy_s3():
    """Deploy to S3 with public access"""
    s3 = boto3.client('s3')
    bucket_name = 'security-dashboard-ui-2025'
    
    try:
        # Create bucket
        try:
            s3.create_bucket(Bucket=bucket_name)
        except:
            pass  # Bucket might already exist
        
        # Upload HTML file
        s3.upload_file(
            'dashboard_simple.html', 
            bucket_name, 
            'index.html',
            ExtraArgs={
                'ContentType': 'text/html',
                'ACL': 'public-read'
            }
        )
        
        # Configure bucket for website hosting
        s3.put_bucket_website(
            Bucket=bucket_name,
            WebsiteConfiguration={
                'IndexDocument': {'Suffix': 'index.html'}
            }
        )
        
        url = f"http://{bucket_name}.s3-website-us-east-1.amazonaws.com"
        print(f"✅ S3 website: {url}")
        return url
        
    except Exception as e:
        print(f"❌ S3 deployment failed: {e}")
        return None

def main():
    print("🚀 Deploying Simple Security Dashboard...")
    
    # Deploy Lambda
    lambda_arn = deploy_lambda()
    
    # Deploy S3 website
    s3_url = deploy_s3()
    
    if s3_url:
        print(f"\n🎉 Dashboard deployed!")
        print(f"📊 Access at: {s3_url}")

if __name__ == "__main__":
    main()
