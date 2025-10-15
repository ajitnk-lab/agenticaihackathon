#!/usr/bin/env python3
import boto3
import zipfile

def deploy_interactive():
    lambda_client = boto3.client('lambda')
    
    with open('dashboard_interactive.html', 'r') as f:
        html_content = f.read().replace('"', '\\"').replace('`', '\\`')
    
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
    
    with zipfile.ZipFile('interactive_lambda.zip', 'w') as z:
        z.writestr('lambda_function.py', lambda_code)
    
    with open('interactive_lambda.zip', 'rb') as f:
        zip_content = f.read()
    
    try:
        lambda_client.delete_function(FunctionName='dashboard-interactive')
    except:
        pass
    
    response = lambda_client.create_function(
        FunctionName='dashboard-interactive',
        Runtime='python3.9',
        Role='arn:aws:iam::039920874011:role/lambda-execution-role',
        Handler='lambda_function.lambda_handler',
        Code={'ZipFile': zip_content},
        Timeout=30
    )
    
    url_response = lambda_client.create_function_url_config(
        FunctionName='dashboard-interactive',
        AuthType='NONE',
        Cors={
            'AllowOrigins': ['*'],
            'AllowMethods': ['GET', 'POST']
        }
    )
    
    lambda_client.add_permission(
        FunctionName='dashboard-interactive',
        StatementId='public-access',
        Action='lambda:InvokeFunctionUrl',
        Principal='*',
        Condition={
            'StringEquals': {
                'lambda:FunctionUrlAuthType': 'NONE'
            }
        }
    )
    
    url = url_response['FunctionUrl']
    print(f"✅ Interactive Dashboard: {url}")
    return url

if __name__ == "__main__":
    deploy_interactive()
