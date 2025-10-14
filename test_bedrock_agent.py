#!/usr/bin/env python3
import boto3
import json
import uuid

def test_bedrock_agent():
    """Simple test of the SecurityOrchestratorAgent"""
    
    client = boto3.client('bedrock-agent-runtime', region_name='us-east-1')
    
    test_prompts = [
        "Analyze security for account 039920874011",
        "What are the security costs?",
        "Give me a security analysis with cost breakdown"
    ]
    
    for i, prompt in enumerate(test_prompts, 1):
        print(f"\n{'='*50}")
        print(f"TEST {i}: {prompt}")
        print('='*50)
        
        try:
            response = client.invoke_agent(
                agentId='LKQIWEYEMZ',
                agentAliasId='TSTALIASID', 
                sessionId=f'test-{uuid.uuid4()}',
                inputText=prompt
            )
            
            # Process streaming response
            result = ""
            for event in response['completion']:
                if 'chunk' in event:
                    chunk = event['chunk']
                    if 'bytes' in chunk:
                        result += chunk['bytes'].decode('utf-8')
            
            print(f"✅ SUCCESS:")
            print(result)
            
        except Exception as e:
            print(f"❌ ERROR: {e}")
    
    print(f"\n{'='*50}")
    print("AGENT TEST COMPLETE")
    print('='*50)

if __name__ == "__main__":
    test_bedrock_agent()
