#!/usr/bin/env python3
"""
Complete Flow Test: Local Python → Lambda → Bedrock Agent → 2 AgentCore Runtimes
Tests the entire architecture end-to-end
"""

import boto3
import json
import time
from datetime import datetime

# AWS Clients
lambda_client = boto3.client('lambda', region_name='us-east-1')
bedrock_agent_runtime = boto3.client('bedrock-agent-runtime', region_name='us-east-1')

# Configuration from deployed resources
LAMBDA_FUNCTION = "security-orchestrator-bedrock-agent"
BEDROCK_AGENT_ID = "QDVHR8CMIW"  # SecurityROICalculatorUpdated (PREPARED)
BEDROCK_AGENT_ALIAS = "TSTALIASID"
ACCOUNT_ID = "039920874011"

def test_lambda_direct():
    """Test 1: Direct Lambda invocation"""
    print("\n" + "="*60)
    print("🧪 TEST 1: Direct Lambda Invocation")
    print("="*60)
    
    payload = {
        'function': 'analyze_security',
        'parameters': [
            {'name': 'account_id', 'value': ACCOUNT_ID}
        ]
    }
    
    response = lambda_client.invoke(
        FunctionName=LAMBDA_FUNCTION,
        InvocationType='RequestResponse',
        Payload=json.dumps(payload)
    )
    
    result = json.loads(response['Payload'].read())
    print(f"✅ Lambda Response:")
    print(f"   Security Score: {result.get('security_score')}")
    print(f"   Data Source: {result.get('data_source')}")
    print(f"   Compliance: {result.get('compliance_status')}")
    return result

def test_bedrock_agent():
    """Test 2: Bedrock Agent invocation (which calls Lambda)"""
    print("\n" + "="*60)
    print("🧪 TEST 2: Bedrock Agent → Lambda")
    print("="*60)
    
    session_id = f"test-{int(time.time())}"
    
    try:
        response = bedrock_agent_runtime.invoke_agent(
            agentId=BEDROCK_AGENT_ID,
            agentAliasId=BEDROCK_AGENT_ALIAS,
            sessionId=session_id,
            inputText=f'Analyze security posture for account {ACCOUNT_ID}'
        )
        
        # Collect streaming response
        full_response = ""
        for event in response['completion']:
            if 'chunk' in event:
                chunk = event['chunk']
                if 'bytes' in chunk:
                    text = chunk['bytes'].decode('utf-8')
                    full_response += text
        
        print(f"✅ Bedrock Agent Response:")
        print(f"   {full_response[:200]}...")
        return full_response
        
    except Exception as e:
        print(f"❌ Bedrock Agent Error: {e}")
        return None

def test_agentcore_integration():
    """Test 3: Verify AgentCore runtime integration"""
    print("\n" + "="*60)
    print("🧪 TEST 3: AgentCore Runtime Integration")
    print("="*60)
    
    # Check Lambda environment variables for AgentCore ARNs
    lambda_config = lambda_client.get_function_configuration(
        FunctionName=LAMBDA_FUNCTION
    )
    
    env_vars = lambda_config.get('Environment', {}).get('Variables', {})
    security_agent = env_vars.get('SECURITY_AGENT_ARN', 'NOT_SET')
    cost_agent = env_vars.get('COST_AGENT_ARN', 'NOT_SET')
    
    print(f"✅ AgentCore Runtimes Configured:")
    print(f"   Security Agent: {security_agent}")
    print(f"   Cost Agent: {cost_agent}")
    
    if 'NOT_SET' in [security_agent, cost_agent]:
        print(f"⚠️  Warning: AgentCore ARNs not configured in Lambda")
        return False
    
    return True

def test_memory_primitive():
    """Test 4: Memory Primitive integration"""
    print("\n" + "="*60)
    print("🧪 TEST 4: Memory Primitive (Historical Trends)")
    print("="*60)
    
    payload = {
        'function': 'get_roi_trends',
        'parameters': [
            {'name': 'account_id', 'value': ACCOUNT_ID}
        ]
    }
    
    response = lambda_client.invoke(
        FunctionName=LAMBDA_FUNCTION,
        InvocationType='RequestResponse',
        Payload=json.dumps(payload)
    )
    
    result = json.loads(response['Payload'].read())
    print(f"✅ Memory Primitive Response:")
    print(f"   Status: {result.get('memory_primitive_status')}")
    print(f"   Trend: {result.get('historical_analysis', {}).get('trend')}")
    print(f"   Data Points: {result.get('historical_analysis', {}).get('data_points')}")
    return result

def run_complete_flow_test():
    """Run all tests in sequence"""
    print("\n" + "🚀"*30)
    print("COMPLETE FLOW TEST")
    print("Local Python → Lambda → Bedrock Agent → AgentCore Runtimes")
    print("🚀"*30)
    
    results = {
        'timestamp': datetime.now().isoformat(),
        'tests': {}
    }
    
    # Test 1: Direct Lambda
    try:
        lambda_result = test_lambda_direct()
        results['tests']['lambda_direct'] = 'PASS' if lambda_result else 'FAIL'
    except Exception as e:
        print(f"❌ Lambda test failed: {e}")
        results['tests']['lambda_direct'] = 'FAIL'
    
    # Test 2: Bedrock Agent
    try:
        agent_result = test_bedrock_agent()
        results['tests']['bedrock_agent'] = 'PASS' if agent_result else 'FAIL'
    except Exception as e:
        print(f"❌ Bedrock Agent test failed: {e}")
        results['tests']['bedrock_agent'] = 'FAIL'
    
    # Test 3: AgentCore Integration
    try:
        agentcore_ok = test_agentcore_integration()
        results['tests']['agentcore_integration'] = 'PASS' if agentcore_ok else 'FAIL'
    except Exception as e:
        print(f"❌ AgentCore test failed: {e}")
        results['tests']['agentcore_integration'] = 'FAIL'
    
    # Test 4: Memory Primitive
    try:
        memory_result = test_memory_primitive()
        results['tests']['memory_primitive'] = 'PASS' if memory_result else 'FAIL'
    except Exception as e:
        print(f"❌ Memory test failed: {e}")
        results['tests']['memory_primitive'] = 'FAIL'
    
    # Summary
    print("\n" + "="*60)
    print("📊 TEST SUMMARY")
    print("="*60)
    for test_name, status in results['tests'].items():
        emoji = "✅" if status == "PASS" else "❌"
        print(f"{emoji} {test_name}: {status}")
    
    total_tests = len(results['tests'])
    passed_tests = sum(1 for s in results['tests'].values() if s == 'PASS')
    
    print(f"\n🏆 Results: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("✅ ALL TESTS PASSED - Complete flow working!")
    else:
        print("⚠️  Some tests failed - review output above")
    
    return results

if __name__ == "__main__":
    results = run_complete_flow_test()
    
    # Save results
    with open('/tmp/flow_test_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n📄 Results saved to: /tmp/flow_test_results.json")
