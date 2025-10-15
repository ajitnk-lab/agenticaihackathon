#!/usr/bin/env python3
"""Verify Bedrock Agent is working after model access granted"""

import boto3
import json

def test_agent_after_access():
    """Test agent after model access is granted"""
    
    print("🤖 Testing Bedrock Agent (after model access)...")
    
    try:
        bedrock_agent = boto3.client('bedrock-agent-runtime', region_name='us-east-1')
        
        response = bedrock_agent.invoke_agent(
            agentId='LKQIWEYEMZ',
            agentAliasId='TSTALIASID', 
            sessionId='test-after-access',
            inputText='Analyze security posture and get costs for account 039920874011'
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
        print(f"❌ Agent still failing: {e}")
        return False

if __name__ == "__main__":
    test_agent_after_access()
