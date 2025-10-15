#!/usr/bin/env python3
"""Test new Bedrock Agent"""

import boto3
import json

def test_new_agent():
    """Test the new agent"""
    
    print("🤖 Testing NEW Bedrock Agent...")
    
    try:
        bedrock_agent = boto3.client('bedrock-agent-runtime', region_name='us-east-1')
        
        response = bedrock_agent.invoke_agent(
            agentId='C6ZC4AGYNQ',
            agentAliasId='TSTALIASID', 
            sessionId='test-new-agent',
            inputText='Analyze security posture for account 039920874011'
        )
        
        print("✅ Bedrock Agent SUCCESS!")
        
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
        print(f"❌ Agent failed: {e}")
        return False

if __name__ == "__main__":
    test_new_agent()
