#!/usr/bin/env python3
"""
Deploy Bedrock Agent Chatbot UI
Creates chatbot that uses proper Bedrock Agent orchestration
"""

import boto3
import zipfile
import io
import os
import json

def create_chatbot_ui(backend_url):
    """Create chatbot UI HTML with backend URL"""
    
    # Read the chatbot HTML template
    with open('chatbot.html', 'r') as f:
        html_content = f.read()
    
    # Replace backend URL placeholder
    html_content = html_content.replace('BEDROCK_AGENT_BACKEND_URL', backend_url)
    
    return html_content

def deploy_backend():
    """Deploy Bedrock Agent backend Lambda"""
    
    lambda_client = boto3.client('lambda')
    
    # Create deployment package
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, 'w') as z:
        # Add backend Lambda code
        z.write('bedrock_agent_backend.py', 'lambda_function.py')
        
        # Add AgentCore source files
        src_path = '../src'
        if os.path.exists(src_path):
            for root, dirs, files in os.walk(src_path):
                for file in files:
                    if file.endswith('.py'):
                        file_path = os.path.join(root, file)
                        arc_path = os.path.relpath(file_path, '..')
                        z.write(file_path, arc_path)
    
    buffer.seek(0)
    
    function_name = 'bedrock-agent-chatbot-backend'
    
    try:
        # Try to update existing function
        try:
            response = lambda_client.update_function_code(
                FunctionName=function_name,
                ZipFile=buffer.read()
            )
            print(f"✅ Updated backend function: {function_name}")
            
        except lambda_client.exceptions.ResourceNotFoundException:
            # Create new function
            buffer.seek(0)
            response = lambda_client.create_function(
                FunctionName=function_name,
                Runtime='python3.9',
                Role='arn:aws:iam::039920874011:role/lambda-execution-role',
                Handler='lambda_function.lambda_handler',
                Code={'ZipFile': buffer.read()},
                Description='Bedrock Agent Chatbot Backend',
                Timeout=60,  # Longer timeout for Bedrock Agent calls
                MemorySize=512
            )
            print(f"✅ Created backend function: {function_name}")
        
        # Create or get function URL
        try:
            url_response = lambda_client.create_function_url_config(
                FunctionName=function_name,
                AuthType='NONE',
                Cors={
                    'AllowCredentials': False,
                    'AllowHeaders': ['*'],
                    'AllowMethods': ['*'],
                    'AllowOrigins': ['*']
                }
            )
            backend_url = url_response['FunctionUrl']
            
        except lambda_client.exceptions.ResourceConflictException:
            url_response = lambda_client.get_function_url_config(FunctionName=function_name)
            backend_url = url_response['FunctionUrl']
        
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
            pass
        
        return backend_url
        
    except Exception as e:
        print(f"❌ Backend deployment error: {e}")
        return None

def deploy_chatbot_ui(backend_url):
    """Deploy chatbot UI Lambda"""
    
    lambda_client = boto3.client('lambda')
    
    # Create UI HTML with backend URL
    html_content = create_chatbot_ui(backend_url)
    
    # Create Lambda function code
    lambda_code = f'''
import json

def lambda_handler(event, context):
    return {{
        'statusCode': 200,
        'headers': {{
            'Content-Type': 'text/html',
            'Cache-Control': 'no-cache'
        }},
        'body': """{html_content}"""
    }}
'''

    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, 'w') as z:
        z.writestr('lambda_function.py', lambda_code)
    
    buffer.seek(0)
    
    function_name = 'bedrock-agent-chatbot-ui'
    
    try:
        # Try to update existing function
        try:
            response = lambda_client.update_function_code(
                FunctionName=function_name,
                ZipFile=buffer.read()
            )
            print(f"✅ Updated UI function: {function_name}")
            
        except lambda_client.exceptions.ResourceNotFoundException:
            # Create new function
            buffer.seek(0)
            response = lambda_client.create_function(
                FunctionName=function_name,
                Runtime='python3.9',
                Role='arn:aws:iam::039920874011:role/lambda-execution-role',
                Handler='lambda_function.lambda_handler',
                Code={'ZipFile': buffer.read()},
                Description='Bedrock Agent Chatbot UI',
                Timeout=30,
                MemorySize=128
            )
            print(f"✅ Created UI function: {function_name}")
        
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
            pass
        
        return ui_url
        
    except Exception as e:
        print(f"❌ UI deployment error: {e}")
        return None

def check_bedrock_agent():
    """Check if Bedrock Agent exists"""
    
    try:
        bedrock_agent = boto3.client('bedrock-agent', region_name='us-east-1')
        
        # List agents to see if any exist
        response = bedrock_agent.list_agents()
        agents = response.get('agentSummaries', [])
        
        if agents:
            agent = agents[0]  # Use first agent found
            agent_id = agent['agentId']
            agent_name = agent['agentName']
            print(f"✅ Found Bedrock Agent: {agent_name} ({agent_id})")
            return agent_id
        else:
            print("⚠️ No Bedrock Agent found. Will use AgentCore fallback.")
            return None
            
    except Exception as e:
        print(f"⚠️ Cannot check Bedrock Agent: {e}. Will use AgentCore fallback.")
        return None

def update_backend_with_agent_id(agent_id):
    """Update backend Lambda with actual Bedrock Agent ID"""
    
    if not agent_id:
        print("ℹ️ No Bedrock Agent ID to update")
        return
    
    try:
        # Read backend code
        with open('bedrock_agent_backend.py', 'r') as f:
            backend_code = f.read()
        
        # Replace placeholder with actual agent ID
        backend_code = backend_code.replace("agent_id = 'YOUR_AGENT_ID'", f"agent_id = '{agent_id}'")
        
        # Update Lambda function
        lambda_client = boto3.client('lambda')
        
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, 'w') as z:
            z.writestr('lambda_function.py', backend_code)
            
            # Add AgentCore source files
            src_path = '../src'
            if os.path.exists(src_path):
                for root, dirs, files in os.walk(src_path):
                    for file in files:
                        if file.endswith('.py'):
                            file_path = os.path.join(root, file)
                            arc_path = os.path.relpath(file_path, '..')
                            z.write(file_path, arc_path)
        
        buffer.seek(0)
        
        lambda_client.update_function_code(
            FunctionName='bedrock-agent-chatbot-backend',
            ZipFile=buffer.read()
        )
        
        print(f"✅ Updated backend with Bedrock Agent ID: {agent_id}")
        
    except Exception as e:
        print(f"⚠️ Could not update backend with Agent ID: {e}")

def main():
    """Deploy complete Bedrock Agent chatbot"""
    
    print("🤖 Deploying Bedrock Agent Chatbot...")
    print("🔄 This implements proper Bedrock Agent → AgentCore orchestration")
    
    # Check for existing Bedrock Agent
    print("\n1. Checking for Bedrock Agent...")
    agent_id = check_bedrock_agent()
    
    # Deploy backend
    print("\n2. Deploying Backend Lambda...")
    backend_url = deploy_backend()
    
    if not backend_url:
        print("❌ Backend deployment failed")
        return
    
    # Update backend with agent ID if found
    if agent_id:
        print("\n3. Configuring Bedrock Agent integration...")
        update_backend_with_agent_id(agent_id)
    
    # Deploy UI
    print("\n4. Deploying Chatbot UI...")
    ui_url = deploy_chatbot_ui(backend_url)
    
    if not ui_url:
        print("❌ UI deployment failed")
        return
    
    print("\n🎉 Bedrock Agent Chatbot Deployment Complete!")
    print(f"🤖 Chatbot UI: {ui_url}")
    print(f"📡 Backend API: {backend_url}")
    
    if agent_id:
        print(f"🧠 Bedrock Agent: {agent_id}")
        print("\n✅ Architecture: UI → Bedrock Agent → AgentCore Agents → AWS APIs")
    else:
        print("\n⚠️ Fallback Mode: UI → AgentCore Agents → AWS APIs")
        print("💡 To enable full Bedrock Agent orchestration:")
        print("   1. Run: python3 ../scripts/create_bedrock_agent.py")
        print("   2. Redeploy this chatbot")
    
    print("\n🗣️ Try asking:")
    print("   • 'What is my current security posture?'")
    print("   • 'Show me critical security findings'")
    print("   • 'What am I spending on security services?'")
    print("   • 'Calculate my security ROI'")
    
    return {
        'chatbot_url': ui_url,
        'backend_url': backend_url,
        'agent_id': agent_id,
        'status': 'success'
    }

if __name__ == "__main__":
    main()
