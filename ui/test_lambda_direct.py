#!/usr/bin/env python3

import boto3
import json

def test_lambda_direct():
    """Test the Lambda function directly with Bedrock Agent event format"""
    
    lambda_client = boto3.client('lambda', region_name='us-east-1')
    
    # Create a test event that matches Bedrock Agent format
    test_event = {
        "sessionId": "test-session-123",
        "sessionAttributes": {},
        "inputText": "Analyze security posture",
        "promptSessionAttributes": {},
        "apiPath": "/analyze_security",
        "agent": {
            "name": "SecurityROICalculatorUpdated",
            "version": "DRAFT",
            "id": "QDVHR8CMIW",
            "alias": "O16RIQ9N82"
        },
        "httpMethod": "GET",
        "messageVersion": "1.0",
        "actionGroup": "SecurityAnalysisActions"
    }
    
    try:
        print("Testing Lambda function directly...")
        print(f"Event: {json.dumps(test_event, indent=2)}")
        
        response = lambda_client.invoke(
            FunctionName='security-orchestrator-lambda',
            Payload=json.dumps(test_event)
        )
        
        # Parse the response
        payload = json.loads(response['Payload'].read())
        
        print("\n📊 Lambda Response:")
        print("=" * 50)
        print(json.dumps(payload, indent=2))
        print("=" * 50)
        print("✅ Lambda test completed successfully!")
        
    except Exception as e:
        print(f"❌ Error testing Lambda: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_lambda_direct()
