#!/usr/bin/env python3
import json
import boto3
import os

SECURITY_AGENT_ARN = os.environ.get('SECURITY_AGENT_ARN', '')
COST_AGENT_ARN = os.environ.get('COST_AGENT_ARN', '')

def call_agentcore(runtime_arn: str, prompt: str):
    try:
        print(f"Calling AgentCore: {runtime_arn}")
        client = boto3.client('bedrock-agentcore', region_name='us-east-1')
        
        response = client.invoke_agent_runtime(
            agentRuntimeArn=runtime_arn,
            contentType='application/json',
            accept='application/json',
            payload=json.dumps({"prompt": prompt}).encode('utf-8')
        )
        
        print(f"Response keys: {response.keys()}")
        
        # Read response - it's in 'response' key, not 'body'
        output = response.get('response', b'')
        if isinstance(output, bytes):
            result = json.loads(output.decode('utf-8')) if output else {}
        else:
            result = output
            
        print(f"Result: {json.dumps(result)}")
        return result
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return {'error': str(e)}

def lambda_handler(event, context):
    try:
        print(f"Event: {event}")
        
        # Bedrock Agent format
        api_path = event.get('apiPath', '')
        account_id = event.get('parameters', [{}])[0].get('value', '039920874011') if event.get('parameters') else '039920874011'
        
        print(f"Function: {api_path}, Account: {account_id}")
        
        prompt = f"analyze_security_posture for account {account_id}"
        result = call_agentcore(SECURITY_AGENT_ARN, prompt)
        
        print(f"Final result: {json.dumps(result)}")
        
        # Return in Bedrock Agent format
        return {
            'messageVersion': '1.0',
            'response': {
                'actionGroup': event.get('actionGroup', ''),
                'apiPath': api_path,
                'httpMethod': event.get('httpMethod', 'GET'),
                'httpStatusCode': 200,
                'responseBody': {
                    'application/json': {
                        'body': json.dumps(result)
                    }
                }
            }
        }
        
    except Exception as e:
        print(f"Lambda error: {e}")
        import traceback
        traceback.print_exc()
        return {'error': str(e)}
