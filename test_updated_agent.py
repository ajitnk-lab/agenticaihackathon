#!/usr/bin/env python3

import boto3
import json

def test_updated_agent():
    """Test the updated Bedrock Agent"""
    
    bedrock_agent_runtime = boto3.client('bedrock-agent-runtime', region_name='us-east-1')
    
    agent_id = 'QDVHR8CMIW'
    alias_id = 'O16RIQ9N82'
    
    try:
        print("Testing updated Bedrock Agent...")
        print(f"Agent ID: {agent_id}")
        print(f"Alias ID: {alias_id}")
        
        # Test the agent
        response = bedrock_agent_runtime.invoke_agent(
            agentId=agent_id,
            agentAliasId=alias_id,
            sessionId='test-session-updated',
            inputText='Please analyze the security posture of my AWS account and calculate the ROI.'
        )
        
        print("\n📊 Agent Response:")
        print("=" * 50)
        
        # Process the streaming response
        for event in response['completion']:
            if 'chunk' in event:
                chunk = event['chunk']
                if 'bytes' in chunk:
                    text = chunk['bytes'].decode('utf-8')
                    print(text, end='')
        
        print("\n" + "=" * 50)
        print("✅ Test completed successfully!")
        
    except Exception as e:
        print(f"❌ Error testing agent: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_updated_agent()
