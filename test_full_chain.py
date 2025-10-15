#!/usr/bin/env python3
"""
Standalone script to test full chain:
Python -> Lambda -> AgentCore -> Real AWS Data
"""

import boto3
import json
import base64

def trigger_lambda_security_analysis():
    """Trigger Lambda function for security analysis"""
    print("🔍 Triggering Lambda Security Analysis...")
    
    lambda_client = boto3.client('lambda', region_name='us-east-1')
    
    # Create payload for Lambda (simulating Bedrock Agent call)
    payload = {
        'actionGroup': 'SecurityActions',
        'apiPath': '/security',
        'httpMethod': 'POST',
        'parameters': [
            {'name': 'account_id', 'value': '039920874011'}
        ]
    }
    
    try:
        response = lambda_client.invoke(
            FunctionName='security-orchestrator-bedrock-agent',
            InvocationType='RequestResponse',
            Payload=json.dumps(payload)
        )
        
        # Parse response
        response_payload = json.loads(response['Payload'].read())
        
        if response['StatusCode'] == 200:
            print("✅ Lambda Security Analysis SUCCESS")
            
            # Extract the actual response body
            response_body = json.loads(
                response_payload['response']['responseBody']['application/json']['body']
            )
            
            print(f"   Security Score: {response_body.get('security_score')}")
            print(f"   Data Source: {response_body.get('data_source')}")
            print(f"   Compliance: {response_body.get('compliance_status')}")
            print(f"   Inspector Findings: {response_body.get('inspector_findings')}")
            
            return response_body
        else:
            print(f"❌ Lambda failed with status: {response['StatusCode']}")
            return None
            
    except Exception as e:
        print(f"❌ Lambda trigger failed: {e}")
        return None

def trigger_lambda_cost_analysis():
    """Trigger Lambda function for cost analysis"""
    print("\n💰 Triggering Lambda Cost Analysis...")
    
    lambda_client = boto3.client('lambda', region_name='us-east-1')
    
    payload = {
        'actionGroup': 'SecurityActions',
        'apiPath': '/cost',
        'httpMethod': 'POST',
        'parameters': [
            {'name': 'account_id', 'value': '039920874011'}
        ]
    }
    
    try:
        response = lambda_client.invoke(
            FunctionName='security-orchestrator-bedrock-agent',
            InvocationType='RequestResponse',
            Payload=json.dumps(payload)
        )
        
        response_payload = json.loads(response['Payload'].read())
        
        if response['StatusCode'] == 200:
            print("✅ Lambda Cost Analysis SUCCESS")
            
            response_body = json.loads(
                response_payload['response']['responseBody']['application/json']['body']
            )
            
            print(f"   Total Cost: ${response_body.get('total_security_cost')}")
            print(f"   Data Source: {response_body.get('data_source')}")
            print(f"   Service Count: {len(response_body.get('service_costs', {}))}")
            
            return response_body
        else:
            print(f"❌ Lambda failed with status: {response['StatusCode']}")
            return None
            
    except Exception as e:
        print(f"❌ Lambda trigger failed: {e}")
        return None

def trigger_lambda_trends():
    """Trigger Lambda function for historical trends"""
    print("\n🧠 Triggering Lambda Historical Trends...")
    
    lambda_client = boto3.client('lambda', region_name='us-east-1')
    
    payload = {
        'actionGroup': 'SecurityActions',
        'apiPath': '/trends',
        'httpMethod': 'POST',
        'parameters': [
            {'name': 'account_id', 'value': '039920874011'}
        ]
    }
    
    try:
        response = lambda_client.invoke(
            FunctionName='security-orchestrator-bedrock-agent',
            InvocationType='RequestResponse',
            Payload=json.dumps(payload)
        )
        
        response_payload = json.loads(response['Payload'].read())
        
        if response['StatusCode'] == 200:
            print("✅ Lambda Historical Trends SUCCESS")
            
            response_body = json.loads(
                response_payload['response']['responseBody']['application/json']['body']
            )
            
            print(f"   Memory Status: {response_body.get('memory_primitive_status')}")
            print(f"   ROI Trend: {response_body.get('historical_analysis', {}).get('trend')}")
            print(f"   Data Points: {response_body.get('historical_analysis', {}).get('data_points')}")
            
            return response_body
        else:
            print(f"❌ Lambda failed with status: {response['StatusCode']}")
            return None
            
    except Exception as e:
        print(f"❌ Lambda trigger failed: {e}")
        return None

def test_bedrock_agent_direct():
    """Test Bedrock Agent directly"""
    print("\n🤖 Testing Bedrock Agent Direct Invocation...")
    
    try:
        bedrock_agent = boto3.client('bedrock-agent-runtime', region_name='us-east-1')
        
        response = bedrock_agent.invoke_agent(
            agentId='LKQIWEYEMZ',
            agentAliasId='TSTALIASID',
            sessionId='test-full-chain',
            inputText='Analyze security posture and costs for account 039920874011'
        )
        
        print("✅ Bedrock Agent Direct Invocation SUCCESS")
        
        # Process streaming response
        full_response = ""
        for event in response['completion']:
            if 'chunk' in event:
                chunk = event['chunk']
                if 'bytes' in chunk:
                    text = chunk['bytes'].decode('utf-8')
                    full_response += text
        
        print(f"   Response Length: {len(full_response)} characters")
        print(f"   Response Preview: {full_response[:200]}...")
        
        return full_response
        
    except Exception as e:
        print(f"❌ Bedrock Agent failed: {e}")
        return None

def main():
    """Run full chain test"""
    print("🚀 Full Chain Test: Python -> Lambda -> AgentCore -> Real AWS Data")
    print("=" * 70)
    
    # Test all components
    security_result = trigger_lambda_security_analysis()
    cost_result = trigger_lambda_cost_analysis()
    trends_result = trigger_lambda_trends()
    agent_result = test_bedrock_agent_direct()
    
    # Summary
    print(f"\n📊 Full Chain Test Results:")
    print(f"   Lambda Security: {'✅ SUCCESS' if security_result else '❌ FAILED'}")
    print(f"   Lambda Cost: {'✅ SUCCESS' if cost_result else '❌ FAILED'}")
    print(f"   Lambda Trends: {'✅ SUCCESS' if trends_result else '❌ FAILED'}")
    print(f"   Bedrock Agent: {'✅ SUCCESS' if agent_result else '❌ FAILED'}")
    
    if security_result and cost_result:
        print(f"\n🎯 Real Data Summary:")
        print(f"   Security Score: {security_result.get('security_score')}/100")
        print(f"   Monthly Cost: ${cost_result.get('total_security_cost')}")
        print(f"   Data Sources: Real AWS services")
        print(f"   Memory Status: {trends_result.get('memory_primitive_status') if trends_result else 'Unknown'}")
    
    success_count = sum([bool(x) for x in [security_result, cost_result, trends_result, agent_result]])
    print(f"\n🏆 Overall Success Rate: {success_count}/4 components working")

if __name__ == "__main__":
    main()
