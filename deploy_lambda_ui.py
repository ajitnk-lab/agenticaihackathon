#!/usr/bin/env python3
import boto3
import zipfile

def deploy_lambda_ui():
    lambda_client = boto3.client('lambda')
    
    # Read HTML content
    with open('dashboard_standalone.html', 'r') as f:
        html_content = f.read().replace('"', '\\"')
    
    # Create Lambda function code
    lambda_code = f'''import json

def lambda_handler(event, context):
    html = """{html_content}"""
    
    return {{
        'statusCode': 200,
        'headers': {{
            'Content-Type': 'text/html',
            'Access-Control-Allow-Origin': '*'
        }},
        'body': html
    }}
'''
    
    # Create zip
    with zipfile.ZipFile('ui_lambda.zip', 'w') as z:
        z.writestr('lambda_function.py', lambda_code)
    
    with open('ui_lambda.zip', 'rb') as f:
        zip_content = f.read()
    
    try:
        # Delete existing
        try:
            lambda_client.delete_function(FunctionName='dashboard-ui')
        except:
            pass
        
        # Create function
        response = lambda_client.create_function(
            FunctionName='dashboard-ui',
            Runtime='python3.9',
            Role='arn:aws:iam::039920874011:role/lambda-execution-role',
            Handler='lambda_function.lambda_handler',
            Code={'ZipFile': zip_content},
            Timeout=30
        )
        
        # Create function URL
        url_response = lambda_client.create_function_url_config(
            FunctionName='dashboard-ui',
            AuthType='NONE',
            Cors={
                'AllowOrigins': ['*'],
                'AllowMethods': ['GET']
            }
        )
        
        url = url_response['FunctionUrl']
        print(f"✅ Dashboard deployed: {url}")
        return url
        
    except Exception as e:
        print(f"❌ Failed: {e}")
        return None

if __name__ == "__main__":
    deploy_lambda_ui()
