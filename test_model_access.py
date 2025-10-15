#!/usr/bin/env python3
"""Test which Claude models have access"""

import boto3
import json

def test_model_access():
    """Test access to different Claude models"""
    
    bedrock = boto3.client('bedrock-runtime', region_name='us-east-1')
    
    models_to_test = [
        "anthropic.claude-3-haiku-20240307-v1:0",
        "anthropic.claude-3-sonnet-20240229-v1:0", 
        "anthropic.claude-3-5-sonnet-20240620-v1:0",
        "anthropic.claude-3-5-sonnet-20241022-v2:0"
    ]
    
    test_payload = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 10,
        "messages": [{"role": "user", "content": "Hi"}]
    }
    
    working_models = []
    
    for model_id in models_to_test:
        try:
            response = bedrock.invoke_model(
                modelId=model_id,
                body=json.dumps(test_payload)
            )
            
            result = json.loads(response['body'].read())
            print(f"✅ {model_id}: WORKS")
            working_models.append(model_id)
            
        except Exception as e:
            print(f"❌ {model_id}: {str(e)[:50]}...")
    
    return working_models

if __name__ == "__main__":
    print("🔍 Testing Claude Model Access...")
    working = test_model_access()
    
    if working:
        print(f"\n✅ Working models: {len(working)}")
        for model in working:
            print(f"   {model}")
    else:
        print(f"\n❌ No Claude models have access granted")
        print(f"   You MUST request model access in Bedrock console")
