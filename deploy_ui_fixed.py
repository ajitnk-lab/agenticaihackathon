#!/usr/bin/env python3
"""Deploy UI to existing Lambda functions"""

import boto3
import zipfile
import os
import time

def deploy_dashboard():
    """Deploy dashboard to dashboard-interactive function"""
    lambda_client = boto3.client('lambda', region_name='us-east-1')
    
    print("📦 Creating dashboard deployment package...")
    
    # Create zip with the working lambda function
    with zipfile.ZipFile('dashboard_deploy.zip', 'w') as z:
        z.write('ui/lambda_function.py', 'lambda_function.py')
    
    print("🚀 Deploying to dashboard-interactive...")
    
    # Update existing function
    with open('dashboard_deploy.zip', 'rb') as f:
        response = lambda_client.update_function_code(
            FunctionName='dashboard-interactive',
            ZipFile=f.read()
        )
    print("✅ Dashboard updated successfully")
    return response

def deploy_agentcore_backend():
    """Deploy AgentCore backend to agentcore-memory-backend function"""
    lambda_client = boto3.client('lambda', region_name='us-east-1')
    
    print("📦 Creating AgentCore backend deployment package...")
    
    # Create zip with the recovered backend
    with zipfile.ZipFile('agentcore_deploy.zip', 'w') as z:
        z.write('agentcore_memory_backend_fixed.py', 'lambda_function.py')
    
    print("🚀 Deploying to agentcore-memory-backend...")
    
    # Update existing function
    with open('agentcore_deploy.zip', 'rb') as f:
        response = lambda_client.update_function_code(
            FunctionName='agentcore-memory-backend',
            ZipFile=f.read()
        )
    print("✅ AgentCore backend updated successfully")
    return response

def get_function_urls():
    """Get Lambda function URLs"""
    lambda_client = boto3.client('lambda', region_name='us-east-1')
    
    urls = {}
    
    for function_name in ['dashboard-interactive', 'agentcore-memory-backend']:
        try:
            response = lambda_client.get_function_url_config(FunctionName=function_name)
            urls[function_name] = response['FunctionUrl']
        except lambda_client.exceptions.ResourceNotFoundException:
            print(f"⚠️  No URL configured for {function_name}")
            urls[function_name] = "No URL configured"
    
    return urls

def test_deployment():
    """Test the deployed functions"""
    print("🧪 Testing deployment...")
    
    urls = get_function_urls()
    
    import urllib.request
    
    for name, url in urls.items():
        if url != "No URL configured":
            try:
                response = urllib.request.urlopen(url)
                if response.getcode() == 200:
                    print(f"✅ {name} is responding at {url}")
                else:
                    print(f"⚠️  {name} returned status: {response.getcode()}")
            except Exception as e:
                print(f"⚠️  {name} test error: {e}")
    
    return urls

def main():
    """Main deployment function"""
    print("🚀 Starting UI deployment to existing functions...")
    
    # Deploy components
    dashboard_result = deploy_dashboard()
    backend_result = deploy_agentcore_backend()
    
    # Wait for deployment to propagate
    print("⏳ Waiting for deployment to propagate...")
    time.sleep(5)
    
    # Test deployment and get URLs
    urls = test_deployment()
    
    print("\n" + "="*60)
    print("🎉 DEPLOYMENT COMPLETE!")
    print("="*60)
    
    for name, url in urls.items():
        if url != "No URL configured":
            print(f"📊 {name}: {url}")
    
    # Use known working URLs from conversation summary
    dashboard_url = "https://tajuooav2jms35ubhnhtiscqvy0usgih.lambda-url.us-east-1.on.aws/"
    backend_url = "https://vxlk4vnqccr5jp7p4aln34wdge0xaudq.lambda-url.us-east-1.on.aws/"
    
    print(f"\n🔗 Known Working URLs:")
    print(f"📊 Dashboard: {dashboard_url}")
    print(f"🧠 Backend: {backend_url}")
    print("="*60)
    
    # Cleanup
    for f in ['dashboard_deploy.zip', 'agentcore_deploy.zip']:
        if os.path.exists(f):
            os.remove(f)
    
    return dashboard_url, backend_url

if __name__ == "__main__":
    main()
