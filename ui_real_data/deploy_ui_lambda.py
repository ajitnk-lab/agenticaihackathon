#!/usr/bin/env python3
"""
Deploy UI as Lambda Function with Function URL
"""

import boto3
import json
from datetime import datetime

def create_ui_lambda():
    """Create Lambda function that serves the UI"""
    
    # Read the HTML file
    with open('dashboard_agentcore_final.html', 'r') as f:
        html_content = f.read()
    
    # Create Lambda function code
    lambda_code = f'''
import json

def lambda_handler(event, context):
    """Serve the AgentCore UI"""
    
    html_content = """{html_content}"""
    
    return {{
        'statusCode': 200,
        'headers': {{
            'Content-Type': 'text/html',
            'Cache-Control': 'no-cache'
        }},
        'body': html_content
    }}
'''
    
    return lambda_code

def deploy_ui():
    """Deploy UI Lambda function"""
    
    lambda_client = boto3.client('lambda')
    
    # Create deployment package
    lambda_code = create_ui_lambda()
    
    function_name = 'security-roi-agentcore-ui'
    
    try:
        # Try to update existing function
        try:
            response = lambda_client.update_function_code(
                FunctionName=function_name,
                ZipFile=create_zip_content(lambda_code)
            )
            print(f"✅ Updated existing UI function: {function_name}")
            
        except lambda_client.exceptions.ResourceNotFoundException:
            # Create new function
            response = lambda_client.create_function(
                FunctionName=function_name,
                Runtime='python3.9',
                Role='arn:aws:iam::039920874011:role/lambda-execution-role',
                Handler='lambda_function.lambda_handler',
                Code={'ZipFile': create_zip_content(lambda_code)},
                Description='AgentCore UI Dashboard',
                Timeout=30,
                MemorySize=128
            )
            print(f"✅ Created new UI function: {function_name}")
        
        # Create or get function URL
        try:
            url_response = lambda_client.create_function_url_config(
                FunctionName=function_name,
                AuthType='NONE',
                Cors={
                    'AllowCredentials': False,
                    'AllowHeaders': ['*'],
                    'AllowMethods': ['GET'],
                    'AllowOrigins': ['*']
                }
            )
            ui_url = url_response['FunctionUrl']
            
        except lambda_client.exceptions.ResourceConflictException:
            # URL already exists, get it
            url_response = lambda_client.get_function_url_config(FunctionName=function_name)
            ui_url = url_response['FunctionUrl']
        
        # Add public access permission
        try:
            lambda_client.add_permission(
                FunctionName=function_name,
                StatementId='FunctionURLAllowPublicAccess',
                Action='lambda:InvokeFunctionUrl',
                Principal='*',
                FunctionUrlAuthType='NONE'
            )
        except:
            pass  # Permission might already exist
        
        print(f"✅ AgentCore UI URL: {ui_url}")
        return ui_url
        
    except Exception as e:
        print(f"❌ Error deploying UI: {e}")
        return None

def create_zip_content(lambda_code):
    """Create zip file content"""
    import zipfile
    import io
    
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, 'w') as z:
        z.writestr('lambda_function.py', lambda_code)
    
    buffer.seek(0)
    return buffer.read()

def main():
    """Deploy AgentCore UI to AWS"""
    
    print("🚀 Deploying AgentCore UI to AWS Lambda...")
    
    ui_url = deploy_ui()
    
    if ui_url:
        print("\n✅ AgentCore UI Deployment Complete!")
        print(f"🌐 UI URL: {ui_url}")
        print(f"📊 Backend URL: https://ypsypowqxwnme2drnpjdeodo5u0swlpk.lambda-url.us-east-1.on.aws/")
        print("\n🤖 This UI gets data ONLY from AgentCore agents")
    else:
        print("❌ UI deployment failed")

if __name__ == "__main__":
    main()
