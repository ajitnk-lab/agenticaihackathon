#!/usr/bin/env python3
"""
Enable Bedrock Model Access
This script attempts to enable model access for Claude models
"""

import boto3
import json

def enable_model_access():
    """Enable model access for Claude models"""
    print("🔓 Attempting to Enable Bedrock Model Access...")
    
    try:
        # This is typically done through the console, but let's try programmatically
        bedrock = boto3.client('bedrock', region_name='us-east-1')
        
        # List available models
        models = bedrock.list_foundation_models()
        claude_models = [m for m in models['modelSummaries'] if 'claude' in m['modelId'].lower()]
        
        print(f"Found {len(claude_models)} Claude models:")
        for model in claude_models:
            print(f"   {model['modelId']} - {model['modelLifecycle']['status']}")
        
        print("\n⚠️  Model access must be requested through AWS Console:")
        print("   1. Go to AWS Bedrock Console")
        print("   2. Click 'Model access' in left sidebar")
        print("   3. Click 'Request model access'")
        print("   4. Select Claude models and submit request")
        print("   5. Access is usually granted instantly")
        
        return False
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_bedrock_agent_with_different_approach():
    """Try different approach to invoke Bedrock Agent"""
    print("\n🤖 Testing Alternative Bedrock Agent Invocation...")
    
    try:
        # Try with different session approach
        bedrock_agent = boto3.client('bedrock-agent-runtime', region_name='us-east-1')
        
        # First create a session
        session_response = bedrock_agent.create_session(
            agentId='LKQIWEYEMZ',
            agentAliasId='TSTALIASID'
        )
        
        session_id = session_response['sessionId']
        print(f"✅ Session created: {session_id}")
        
        # Now try to invoke with the session
        response = bedrock_agent.invoke_agent(
            agentId='LKQIWEYEMZ',
            agentAliasId='TSTALIASID',
            sessionId=session_id,
            inputText='Hello, can you analyze security for account 039920874011?'
        )
        
        print("✅ Bedrock Agent invocation SUCCESS!")
        
        # Process response
        full_response = ""
        for event in response['completion']:
            if 'chunk' in event:
                chunk = event['chunk']
                if 'bytes' in chunk:
                    text = chunk['bytes'].decode('utf-8')
                    full_response += text
        
        print(f"Agent Response: {full_response}")
        return True
        
    except Exception as e:
        print(f"❌ Alternative approach failed: {e}")
        
        # Check if it's specifically a model access issue
        if "AccessDenied" in str(e) and "model" in str(e).lower():
            print("   Root cause: Model access not granted")
            print("   Solution: Request Claude model access in Bedrock console")
        
        return False

def check_agent_configuration():
    """Check if agent configuration is correct"""
    print("\n📋 Checking Agent Configuration...")
    
    try:
        bedrock_agent = boto3.client('bedrock-agent', region_name='us-east-1')
        
        # Get agent details
        agent = bedrock_agent.get_agent(agentId='LKQIWEYEMZ')
        agent_info = agent['agent']
        
        print(f"✅ Agent Status: {agent_info['agentStatus']}")
        print(f"   Foundation Model: {agent_info['foundationModel']}")
        print(f"   Resource Role: {agent_info['agentResourceRoleArn']}")
        
        # Check if the model in the agent config has access
        model_id = agent_info['foundationModel']
        print(f"\n🔍 Agent uses model: {model_id}")
        
        # Try to invoke this specific model
        bedrock_runtime = boto3.client('bedrock-runtime', region_name='us-east-1')
        
        test_payload = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 10,
            "messages": [{"role": "user", "content": "Hi"}]
        }
        
        try:
            response = bedrock_runtime.invoke_model(
                modelId=model_id,
                body=json.dumps(test_payload)
            )
            print(f"✅ Model {model_id} is accessible")
            return True
            
        except Exception as model_error:
            print(f"❌ Model {model_id} access denied: {model_error}")
            print("   This is why the Bedrock Agent fails!")
            return False
        
    except Exception as e:
        print(f"❌ Agent configuration check failed: {e}")
        return False

def main():
    """Main function"""
    print("🔍 Bedrock Agent Access Diagnosis")
    print("=" * 50)
    
    # Run all checks
    enable_model_access()
    agent_config_ok = check_agent_configuration()
    agent_invoke_ok = test_bedrock_agent_with_different_approach()
    
    print(f"\n📊 Diagnosis Results:")
    print(f"   Agent Configuration: {'✅ OK' if agent_config_ok else '❌ ISSUE'}")
    print(f"   Agent Invocation: {'✅ OK' if agent_invoke_ok else '❌ ISSUE'}")
    
    if not agent_config_ok:
        print(f"\n🎯 SOLUTION:")
        print(f"   1. Go to AWS Bedrock Console")
        print(f"   2. Navigate to 'Model access'")
        print(f"   3. Request access to Claude 3.5 Sonnet models")
        print(f"   4. Wait for approval (usually instant)")
        print(f"   5. Test again")

if __name__ == "__main__":
    main()
