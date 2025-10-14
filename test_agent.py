#!/usr/bin/env python3
import boto3
import json
import uuid

def test_bedrock_agent():
    client = boto3.client('bedrock-agent-runtime', region_name='us-east-1')
    
    try:
        response = client.invoke_agent(
            agentId='LKQIWEYEMZ',
            agentAliasId='TSTALIASID',
            sessionId=str(uuid.uuid4()),
            inputText='Analyze security posture for account 039920874011'
        )
        
        # Process the streaming response
        completion = ""
        for event in response['completion']:
            if 'chunk' in event:
                chunk = event['chunk']
                if 'bytes' in chunk:
                    completion += chunk['bytes'].decode('utf-8')
        
        print("Agent Response:")
        print(completion)
        return completion
        
    except Exception as e:
        print(f"Error invoking agent: {e}")
        return None

if __name__ == "__main__":
    test_bedrock_agent()
