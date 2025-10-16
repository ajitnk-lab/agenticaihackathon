#!/usr/bin/env python3
import boto3
import json
import time

def test_agentcore_direct():
    """Test AgentCore runtimes directly"""
    print("🧪 Testing AgentCore Runtimes Directly...")
    
    try:
        client = boto3.client('bedrock-agentcore')
        
        # Test security agent
        security_arn = "arn:aws:bedrock-agentcore:us-east-1:039920874011:runtime/well_architected_security_agentcore-uBgBoaAnRs"
        print(f"Testing Security Agent: {security_arn}")
        
        response = client.invoke_agent_runtime(
            agentRuntimeArn=security_arn,
            payload=json.dumps({"inputText": "analyze_security_posture", "account_id": "039920874011"})
        )
        print(f"✅ Security Agent Response Keys: {response.keys()}")
        
        # Test cost agent
        cost_arn = "arn:aws:bedrock-agentcore:us-east-1:039920874011:runtime/cost_analysis_agentcore-UTdyrMH0Jo"
        print(f"Testing Cost Agent: {cost_arn}")
        
        response = client.invoke_agent_runtime(
            agentRuntimeArn=cost_arn,
            payload=json.dumps({"inputText": "calculate_security_roi", "account_id": "039920874011"})
        )
        print(f"✅ Cost Agent Response Keys: {response.keys()}")
        
        return True
        
    except Exception as e:
        print(f"❌ AgentCore Test Failed: {str(e)}")
        return False

def test_lambda_function():
    """Test Lambda function directly"""
    print("\n🧪 Testing Lambda Function Directly...")
    
    try:
        client = boto3.client('lambda')
        
        # Test security analysis
        test_event = {
            'messageVersion': '1.0',
            'sessionId': 'test-session',
            'agent': {'name': 'SecurityROICalculatorUpdated', 'version': 'DRAFT', 'id': 'QDVHR8CMIW', 'alias': 'TSTALIASID'},
            'actionGroup': 'SecurityAnalysisActions',
            'sessionAttributes': {},
            'promptSessionAttributes': {},
            'inputText': 'Show me my security score',
            'httpMethod': 'GET',
            'apiPath': '/analyze_security'
        }
        
        response = client.invoke(
            FunctionName='security-orchestrator-lambda',
            Payload=json.dumps(test_event)
        )
        
        result = json.loads(response['Payload'].read())
        print(f"✅ Lambda Response: {json.dumps(result, indent=2)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Lambda Test Failed: {str(e)}")
        return False

def test_bedrock_agent():
    """Test Bedrock Agent"""
    print("\n🧪 Testing Bedrock Agent...")
    
    try:
        client = boto3.client('bedrock-agent-runtime')
        
        response = client.create_invocation(
            agentId='QDVHR8CMIW',
            agentAliasId='TSTALIASID',
            sessionId='test-session-' + str(int(time.time())),
            inputText='Show me my security score'
        )
        
        print(f"✅ Bedrock Agent Response: {json.dumps(response, indent=2, default=str)}")
        return True
        
    except Exception as e:
        print(f"❌ Bedrock Agent Test Failed: {str(e)}")
        return False

def check_lambda_logs():
    """Check recent Lambda logs"""
    print("\n📋 Checking Lambda Logs...")
    
    try:
        client = boto3.client('logs')
        
        # Get recent log streams
        streams = client.describe_log_streams(
            logGroupName='/aws/lambda/security-orchestrator-lambda',
            orderBy='LastEventTime',
            descending=True,
            limit=1
        )
        
        if streams['logStreams']:
            latest_stream = streams['logStreams'][0]['logStreamName']
            
            # Get recent events
            events = client.get_log_events(
                logGroupName='/aws/lambda/security-orchestrator-lambda',
                logStreamName=latest_stream,
                startTime=int(time.time() * 1000) - 300000  # Last 5 minutes
            )
            
            print("📋 Recent Log Events:")
            for event in events['events'][-10:]:  # Last 10 events
                print(f"  {event['message'].strip()}")
        
        return True
        
    except Exception as e:
        print(f"❌ Log Check Failed: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 Starting Comprehensive Bedrock Agent Test Suite\n")
    
    # Run all tests
    agentcore_ok = test_agentcore_direct()
    lambda_ok = test_lambda_function()
    bedrock_ok = test_bedrock_agent()
    check_lambda_logs()
    
    print(f"\n📊 Test Results:")
    print(f"  AgentCore Direct: {'✅ PASS' if agentcore_ok else '❌ FAIL'}")
    print(f"  Lambda Function: {'✅ PASS' if lambda_ok else '❌ FAIL'}")
    print(f"  Bedrock Agent: {'✅ PASS' if bedrock_ok else '❌ FAIL'}")
    
    if all([agentcore_ok, lambda_ok, bedrock_ok]):
        print("\n🎉 ALL TESTS PASSED! Bedrock Agent orchestration should work.")
    else:
        print("\n🚨 SOME TESTS FAILED. Issues need to be resolved.")
