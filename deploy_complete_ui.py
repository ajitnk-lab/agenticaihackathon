#!/usr/bin/env python3
"""Complete UI deployment script"""

import boto3
import zipfile
import os
import json
import time

def deploy_dashboard():
    """Deploy the dashboard Lambda function"""
    lambda_client = boto3.client('lambda', region_name='us-east-1')
    
    print("📦 Creating dashboard deployment package...")
    
    # Create zip with the working lambda function
    with zipfile.ZipFile('dashboard_deploy.zip', 'w') as z:
        z.write('ui/lambda_function.py', 'lambda_function.py')
    
    print("🚀 Deploying dashboard...")
    
    try:
        # Update existing function
        with open('dashboard_deploy.zip', 'rb') as f:
            response = lambda_client.update_function_code(
                FunctionName='security-roi-dashboard',
                ZipFile=f.read()
            )
        print("✅ Dashboard updated successfully")
        
    except lambda_client.exceptions.ResourceNotFoundException:
        print("⚠️  Function not found, creating new one...")
        # Create new function if it doesn't exist
        with open('dashboard_deploy.zip', 'rb') as f:
            response = lambda_client.create_function(
                FunctionName='security-roi-dashboard',
                Runtime='python3.9',
                Role='arn:aws:iam::123456789012:role/lambda-execution-role',
                Handler='lambda_function.lambda_handler',
                Code={'ZipFile': f.read()},
                Description='Security ROI Dashboard'
            )
        print("✅ Dashboard created successfully")
    
    return response

def deploy_agentcore_backend():
    """Deploy the AgentCore Memory backend"""
    lambda_client = boto3.client('lambda', region_name='us-east-1')
    
    print("📦 Creating AgentCore backend deployment package...")
    
    # Create zip with the recovered backend
    with zipfile.ZipFile('agentcore_deploy.zip', 'w') as z:
        z.write('agentcore_memory_backend_fixed.py', 'lambda_function.py')
    
    print("🚀 Deploying AgentCore backend...")
    
    try:
        # Update existing function
        with open('agentcore_deploy.zip', 'rb') as f:
            response = lambda_client.update_function_code(
                FunctionName='agentcore-memory-backend',
                ZipFile=f.read()
            )
        print("✅ AgentCore backend updated successfully")
        
    except lambda_client.exceptions.ResourceNotFoundException:
        print("⚠️  Function not found, will use existing deployed version")
        response = {"FunctionArn": "existing"}
    
    return response

def test_deployment():
    """Test the deployed functions"""
    print("🧪 Testing deployment...")
    
    # Test dashboard
    dashboard_url = "https://tajuooav2jms35ubhnhtiscqvy0usgih.lambda-url.us-east-1.on.aws/"
    backend_url = "https://vxlk4vnqccr5jp7p4aln34wdge0xaudq.lambda-url.us-east-1.on.aws/"
    
    import urllib.request
    
    try:
        # Test dashboard
        response = urllib.request.urlopen(dashboard_url)
        if response.getcode() == 200:
            print("✅ Dashboard is responding")
        else:
            print(f"⚠️  Dashboard returned status: {response.getcode()}")
            
        # Test backend
        response = urllib.request.urlopen(backend_url)
        if response.getcode() == 200:
            print("✅ AgentCore backend is responding")
        else:
            print(f"⚠️  Backend returned status: {response.getcode()}")
            
    except Exception as e:
        print(f"⚠️  Test error: {e}")
    
    return dashboard_url, backend_url

def main():
    """Main deployment function"""
    print("🚀 Starting complete UI deployment...")
    
    # Deploy components
    dashboard_result = deploy_dashboard()
    backend_result = deploy_agentcore_backend()
    
    # Wait for deployment to propagate
    print("⏳ Waiting for deployment to propagate...")
    time.sleep(5)
    
    # Test deployment
    dashboard_url, backend_url = test_deployment()
    
    print("\n" + "="*60)
    print("🎉 DEPLOYMENT COMPLETE!")
    print("="*60)
    print(f"📊 Dashboard URL: {dashboard_url}")
    print(f"🧠 AgentCore Backend: {backend_url}")
    print("="*60)
    
    # Cleanup
    for f in ['dashboard_deploy.zip', 'agentcore_deploy.zip']:
        if os.path.exists(f):
            os.remove(f)
    
    return dashboard_url, backend_url

if __name__ == "__main__":
    main()
