#!/usr/bin/env python3
"""
Deploy Real Data UI - connects to actual AgentCore agents
"""

import boto3
import json
import zipfile
import os
import time

def create_deployment_package():
    """Create deployment package with real backend"""
    
    # Create zip file
    zip_path = 'real_ui_deployment.zip'
    
    with zipfile.ZipFile(zip_path, 'w') as zip_file:
        # Add backend Lambda
        zip_file.write('backend_real.py', 'lambda_function.py')
        
        # Add AgentCore source files
        src_dir = '../src'
        if os.path.exists(src_dir):
            for root, dirs, files in os.walk(src_dir):
                for file in files:
                    if file.endswith('.py'):
                        file_path = os.path.join(root, file)
                        arc_path = os.path.relpath(file_path, '..')
                        zip_file.write(file_path, arc_path)
    
    return zip_path

def deploy_real_backend():
    """Deploy backend Lambda that uses real AgentCore agents"""
    
    lambda_client = boto3.client('lambda')
    
    # Create deployment package
    zip_path = create_deployment_package()
    
    function_name = 'security-roi-real-backend'
    
    try:
        with open(zip_path, 'rb') as zip_file:
            zip_content = zip_file.read()
        
        # Try to update existing function
        try:
            response = lambda_client.update_function_code(
                FunctionName=function_name,
                ZipFile=zip_content
            )
            print(f"✅ Updated existing function: {function_name}")
            
        except lambda_client.exceptions.ResourceNotFoundException:
            # Create new function
            response = lambda_client.create_function(
                FunctionName=function_name,
                Runtime='python3.9',
                Role='arn:aws:iam::039920874011:role/lambda-execution-role',
                Handler='lambda_function.lambda_handler',
                Code={'ZipFile': zip_content},
                Description='Real data backend for Security ROI Dashboard',
                Timeout=30,
                MemorySize=256
            )
            print(f"✅ Created new function: {function_name}")
        
        # Create or update function URL
        try:
            url_response = lambda_client.create_function_url_config(
                FunctionName=function_name,
                AuthType='NONE',
                Cors={
                    'AllowCredentials': False,
                    'AllowHeaders': ['*'],
                    'AllowMethods': ['GET', 'POST'],
                    'AllowOrigins': ['*']
                }
            )
            backend_url = url_response['FunctionUrl']
            
        except lambda_client.exceptions.ResourceConflictException:
            # URL already exists, get it
            url_response = lambda_client.get_function_url_config(FunctionName=function_name)
            backend_url = url_response['FunctionUrl']
        
        print(f"✅ Real Backend URL: {backend_url}")
        
        # Clean up
        os.remove(zip_path)
        
        return backend_url
        
    except Exception as e:
        print(f"❌ Error deploying real backend: {e}")
        return None

def update_dashboard_with_backend_url(backend_url):
    """Update dashboard HTML with real backend URL"""
    
    with open('dashboard_real.html', 'r') as f:
        html_content = f.read()
    
    # Replace placeholder with actual URL
    updated_html = html_content.replace('REPLACE_WITH_REAL_BACKEND_URL', backend_url)
    
    with open('dashboard_real_updated.html', 'w') as f:
        f.write(updated_html)
    
    print(f"✅ Updated dashboard saved as: dashboard_real_updated.html")

def main():
    """Deploy complete real data UI"""
    
    print("🚀 Deploying Real Data UI...")
    print("📊 This UI connects to REAL AgentCore agents with memory integration")
    
    # Deploy real backend
    backend_url = deploy_real_backend()
    
    if backend_url:
        # Update dashboard with backend URL
        update_dashboard_with_backend_url(backend_url)
        
        print("\n✅ Real Data UI Deployment Complete!")
        print(f"📊 Backend (Real Agents): {backend_url}")
        print("📄 Frontend: Use dashboard_real_updated.html")
        print("\n🔴 This UI shows REAL AWS security data from AgentCore agents")
    else:
        print("❌ Deployment failed")

if __name__ == "__main__":
    main()
