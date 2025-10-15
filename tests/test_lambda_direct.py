#!/usr/bin/env python3
import boto3
import json

lambda_client = boto3.client('lambda', region_name='us-east-1')

payload = {
    'function': 'analyze_security',
    'parameters': [{'name': 'account_id', 'value': '039920874011'}]
}

print("Invoking Lambda...")
response = lambda_client.invoke(
    FunctionName='security-orchestrator-bedrock-agent',
    InvocationType='RequestResponse',
    Payload=json.dumps(payload)
)

result = json.loads(response['Payload'].read())
print(f"\nResponse: {json.dumps(result, indent=2)}")
