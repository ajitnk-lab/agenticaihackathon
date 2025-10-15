#!/usr/bin/env python3
"""Detailed Bedrock Agent Testing"""

import boto3
import json

def test_model_access():
    """Test direct model access"""
    print("🔍 Testing Model Access...")
    
    try:
        bedrock = boto3.client('bedrock-runtime', region_name='us-east-1')
        
        # Test with Claude 3.5 Sonnet
        response = bedrock.invoke_model(
            modelId='anthropic.claude-3-5-sonnet-20240620-v1:0',
            body=json.dumps({
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 100,
                "messages": [{"role": "user", "content": "Hello"}]
            })
        )
        
        result = json.loads(response['body'].read())
        print(f"✅ Model Access: SUCCESS")
        print(f"   Response: {result.get('content', [{}])[0].get('text', 'No text')[:50]}...")
        return True
        
    except Exception as e:
        print(f"❌ Model Access: {e}")
        return False

def test_agent_permissions():
    """Test Bedrock Agent permissions"""
    print("\n🤖 Testing Bedrock Agent Permissions...")
    
    try:
        bedrock_agent = boto3.client('bedrock-agent-runtime', region_name='us-east-1')
        
        # Test agent invocation
        response = bedrock_agent.invoke_agent(
            agentId='LKQIWEYEMZ',
            agentAliasId='TSTALIASID',
            sessionId='test-session-detailed',
            inputText='Hello'
        )
        
        print("✅ Agent Permissions: SUCCESS")
        return True
        
    except Exception as e:
        print(f"❌ Agent Permissions: {e}")
        
        # Check if it's a specific permission issue
        if "AccessDenied" in str(e):
            print("   Issue: Access denied - need model access or agent permissions")
        elif "ValidationException" in str(e):
            print("   Issue: Validation error - check agent ID/alias")
        elif "ResourceNotFound" in str(e):
            print("   Issue: Agent not found")
        else:
            print(f"   Issue: Unknown error - {type(e).__name__}")
        
        return False

def test_agent_details():
    """Get agent details"""
    print("\n📋 Testing Agent Details...")
    
    try:
        bedrock_agent = boto3.client('bedrock-agent', region_name='us-east-1')
        
        # Get agent details
        agent = bedrock_agent.get_agent(agentId='LKQIWEYEMZ')
        print(f"✅ Agent Status: {agent['agent']['agentStatus']}")
        print(f"   Foundation Model: {agent['agent']['foundationModel']}")
        print(f"   Resource Role: {agent['agent']['agentResourceRoleArn']}")
        
        # Get alias details
        alias = bedrock_agent.get_agent_alias(agentId='LKQIWEYEMZ', agentAliasId='TSTALIASID')
        print(f"✅ Alias Status: {alias['agentAlias']['agentAliasStatus']}")
        print(f"   Invocation State: {alias['agentAlias']['aliasInvocationState']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Agent Details: {e}")
        return False

def test_iam_permissions():
    """Test IAM permissions"""
    print("\n🔐 Testing IAM Permissions...")
    
    try:
        sts = boto3.client('sts')
        identity = sts.get_caller_identity()
        
        print(f"✅ Identity: {identity['Arn']}")
        print(f"   Account: {identity['Account']}")
        print(f"   User ID: {identity['UserId']}")
        
        # Test Bedrock permissions
        bedrock = boto3.client('bedrock', region_name='us-east-1')
        models = bedrock.list_foundation_models()
        print(f"✅ Bedrock Access: Can list {len(models['modelSummaries'])} models")
        
        return True
        
    except Exception as e:
        print(f"❌ IAM Permissions: {e}")
        return False

def main():
    """Run all tests"""
    print("🔍 Comprehensive Bedrock Agent Testing")
    print("=" * 50)
    
    tests = [
        test_iam_permissions,
        test_agent_details,
        test_model_access,
        test_agent_permissions
    ]
    
    results = []
    for test in tests:
        results.append(test())
    
    print(f"\n📊 Test Results: {sum(results)}/{len(results)} passed")
    
    if not results[2]:  # Model access failed
        print("\n💡 Solution: Request model access in Bedrock console:")
        print("   1. Go to AWS Bedrock console")
        print("   2. Navigate to 'Model access'")
        print("   3. Request access to Claude models")
        print("   4. Wait for approval (usually instant)")

if __name__ == "__main__":
    main()
