#!/usr/bin/env python3
"""Test inference profile access"""

import boto3
import json

def test_inference_profiles():
    """Test inference profile models"""
    
    bedrock = boto3.client('bedrock-runtime', region_name='us-east-1')
    
    # Test inference profile models
    inference_models = [
        "us.anthropic.claude-3-5-sonnet-20241022-v2:0",
        "us.anthropic.claude-3-5-sonnet-20240620-v1:0",
        "us.anthropic.claude-3-haiku-20240307-v1:0"
    ]
    
    test_payload = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 10,
        "messages": [{"role": "user", "content": "Hi"}]
    }
    
    for model_id in inference_models:
        try:
            response = bedrock.invoke_model(
                modelId=model_id,
                body=json.dumps(test_payload)
            )
            
            result = json.loads(response['body'].read())
            print(f"✅ {model_id}: WORKS!")
            print(f"   Response: {result.get('content', [{}])[0].get('text', 'No text')}")
            return model_id
            
        except Exception as e:
            print(f"❌ {model_id}: {str(e)[:60]}...")
    
    return None

def test_agent_with_working_model():
    """Test agent after confirming model access"""
    
    print("\n🤖 Testing Bedrock Agent...")
    
    try:
        bedrock_agent = boto3.client('bedrock-agent-runtime', region_name='us-east-1')
        
        response = bedrock_agent.invoke_agent(
            agentId='LKQIWEYEMZ',
            agentAliasId='TSTALIASID',
            sessionId='test-working-model',
            inputText='Hello! Can you analyze security for account 039920874011?'
        )
        
        print("✅ Bedrock Agent WORKING!")
        
        # Process streaming response
        full_response = ""
        for event in response['completion']:
            if 'chunk' in event:
                chunk = event['chunk']
                if 'bytes' in chunk:
                    text = chunk['bytes'].decode('utf-8')
                    full_response += text
                    print(text, end='', flush=True)
        
        print(f"\n\n🎉 AGENT RESPONSE COMPLETE!")
        return True
        
    except Exception as e:
        print(f"❌ Agent failed: {e}")
        return False

if __name__ == "__main__":
    print("🔍 Testing Model Access and Agent...")
    
    working_model = test_inference_profiles()
    
    if working_model:
        print(f"\n✅ Model access confirmed: {working_model}")
        test_agent_with_working_model()
    else:
        print(f"\n❌ No model access yet - may need a few minutes to propagate")
        print(f"   Try again in 2-3 minutes")
