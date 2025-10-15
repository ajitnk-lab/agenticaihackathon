#!/usr/bin/env python3
"""Test Bedrock Agent with updated Lambda"""

import boto3
import json

def test_bedrock_agent():
    """Test Bedrock Agent invocation"""
    
    bedrock_agent = boto3.client('bedrock-agent-runtime', region_name='us-east-1')
    
    try:
        response = bedrock_agent.invoke_agent(
            agentId='LKQIWEYEMZ',
            agentAliasId='TSTALIASID',
            sessionId='test-session-real-data',
            inputText='Analyze security posture for account 039920874011'
        )
        
        # Process streaming response
        for event in response['completion']:
            if 'chunk' in event:
                chunk = event['chunk']
                if 'bytes' in chunk:
                    text = chunk['bytes'].decode('utf-8')
                    print(text, end='')
        
        print("\n\n✅ Bedrock Agent test completed")
        
    except Exception as e:
        print(f"❌ Bedrock Agent test failed: {e}")

if __name__ == "__main__":
    print("🤖 Testing Bedrock Agent with Updated Lambda (Real Data)")
    print("=" * 60)
    test_bedrock_agent()
