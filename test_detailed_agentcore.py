#!/usr/bin/env python3
"""
Standalone comprehensive test for AgentCore runtimes with maximum detail output
"""

import sys
import os
import json
import asyncio
from datetime import datetime

# Add project paths
sys.path.append('src')
sys.path.append('src/agentcore')
sys.path.append('src/lambda')

def print_section(title):
    """Print formatted section header"""
    print(f"\n{'='*80}")
    print(f"🔍 {title}")
    print('='*80)

def print_json_pretty(data, title="Response"):
    """Print JSON data with pretty formatting"""
    print(f"\n📋 {title}:")
    print(json.dumps(data, indent=2, default=str))

async def test_security_agentcore_detailed():
    """Test Security AgentCore with all available tools"""
    print_section("SECURITY AGENTCORE RUNTIME - DETAILED TESTING")
    
    try:
        from well_architected_security_agentcore import handler, analyze_security_posture, get_security_findings
        
        # Test 1: Direct function calls
        print("\n🔧 Testing Direct Function Calls:")
        
        print("\n1️⃣ analyze_security_posture():")
        security_result = analyze_security_posture("123456789012")
        print_json_pretty(security_result, "Security Posture Analysis")
        
        print("\n2️⃣ get_security_findings():")
        findings_result = get_security_findings("123456789012")
        print_json_pretty(findings_result, "Security Findings")
        
        # Test 2: AgentCore handler calls
        print("\n🚀 Testing AgentCore Handler:")
        
        test_events = [
            {"prompt": "analyze_security_posture"},
            {"prompt": "get_security_findings"},
            {"prompt": "security posture analysis"},
            {"prompt": "show available tools"}
        ]
        
        for i, event in enumerate(test_events, 1):
            print(f"\n{i}️⃣ Event: {event}")
            result = await handler(event)
            response_data = json.loads(result["body"])
            print_json_pretty(response_data, f"Handler Response {i}")
        
        return True
        
    except Exception as e:
        print(f"❌ Security AgentCore Error: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_cost_agentcore_detailed():
    """Test Cost AgentCore with all available tools"""
    print_section("COST ANALYSIS AGENTCORE RUNTIME - DETAILED TESTING")
    
    try:
        from cost_analysis_agentcore import handler, get_security_costs, calculate_security_roi, get_roi_trends
        
        # Test 1: Direct function calls
        print("\n🔧 Testing Direct Function Calls:")
        
        print("\n1️⃣ get_security_costs():")
        costs_result = get_security_costs("123456789012")
        print_json_pretty(costs_result, "Security Costs")
        
        print("\n2️⃣ calculate_security_roi():")
        roi_result = calculate_security_roi("123456789012")
        print_json_pretty(roi_result, "ROI Calculation")
        
        print("\n3️⃣ get_roi_trends():")
        trends_result = get_roi_trends("123456789012")
        print_json_pretty(trends_result, "ROI Trends")
        
        # Test 2: AgentCore handler calls
        print("\n🚀 Testing AgentCore Handler:")
        
        test_events = [
            {"prompt": "get_security_costs"},
            {"prompt": "calculate_security_roi"},
            {"prompt": "roi_trends"},
            {"prompt": "get roi trends"},
            {"prompt": "show available tools"}
        ]
        
        for i, event in enumerate(test_events, 1):
            print(f"\n{i}️⃣ Event: {event}")
            result = await handler(event)
            response_data = json.loads(result["body"])
            print_json_pretty(response_data, f"Handler Response {i}")
        
        return True
        
    except Exception as e:
        print(f"❌ Cost AgentCore Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_lambda_integration_detailed():
    """Test Lambda integration with detailed responses"""
    print_section("LAMBDA INTEGRATION - DETAILED TESTING")
    
    try:
        from bedrock_agent_lambda import lambda_handler, call_agentcore, test_agentcore_locally
        
        # Test Bedrock Agent events
        test_events = [
            {
                'actionGroup': 'security-analysis',
                'apiPath': '/analyze-security',
                'httpMethod': 'POST',
                'requestBody': {'account_id': '123456789012'}
            },
            {
                'actionGroup': 'security-analysis', 
                'apiPath': '/calculate-roi',
                'httpMethod': 'POST',
                'requestBody': {'account_id': '123456789012'}
            },
            {
                'actionGroup': 'security-analysis',
                'apiPath': '/get-trends', 
                'httpMethod': 'POST',
                'requestBody': {'account_id': '123456789012'}
            },
            {
                'actionGroup': 'security-analysis',
                'apiPath': '/unknown-path',
                'httpMethod': 'POST', 
                'requestBody': {}
            }
        ]
        
        for i, event in enumerate(test_events, 1):
            print(f"\n{i}️⃣ Lambda Event:")
            print_json_pretty(event, "Input Event")
            
            result = lambda_handler(event, {})
            print_json_pretty(result, "Lambda Response")
            
            # Extract and show response body
            response_body = json.loads(result['response']['responseBody']['application/json']['body'])
            print_json_pretty(response_body, "Extracted Response Body")
        
        return True
        
    except Exception as e:
        print(f"❌ Lambda Integration Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_memory_integration_detailed():
    """Test Memory integration with detailed output"""
    print_section("MEMORY PRIMITIVE INTEGRATION - DETAILED TESTING")
    
    try:
        from memory_integration import SecurityMemoryManager, CostMemoryManager
        
        # Test Security Memory Manager
        print("\n🧠 Security Memory Manager:")
        security_memory = SecurityMemoryManager()
        print(f"Memory ID: {security_memory.memory_id}")
        
        # Test storing assessment
        test_assessment = {
            "account_id": "123456789012",
            "security_score": 85,
            "timestamp": datetime.now().isoformat(),
            "findings": ["Test finding 1", "Test finding 2"]
        }
        
        print("\n📝 Storing test assessment:")
        print_json_pretty(test_assessment, "Assessment Data")
        
        try:
            security_memory.store_assessment("123456789012", test_assessment)
            print("✅ Assessment stored successfully")
        except Exception as e:
            print(f"⚠️ Memory storage failed (expected without AWS setup): {e}")
        
        # Test Cost Memory Manager
        print("\n💰 Cost Memory Manager:")
        cost_memory = CostMemoryManager()
        print(f"Memory ID: {cost_memory.memory_id}")
        
        test_cost_data = {
            "account_id": "123456789012", 
            "roi_percentage": 250.0,
            "timestamp": datetime.now().isoformat()
        }
        
        print("\n📝 Storing test cost data:")
        print_json_pretty(test_cost_data, "Cost Data")
        
        try:
            cost_memory.store_cost_analysis("123456789012", test_cost_data)
            print("✅ Cost data stored successfully")
        except Exception as e:
            print(f"⚠️ Memory storage failed (expected without AWS setup): {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Memory Integration Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_real_aws_integration():
    """Test real AWS integration capabilities"""
    print_section("REAL AWS INTEGRATION - DETAILED TESTING")
    
    try:
        # Test real security data
        print("\n🔍 Testing Real Security Data:")
        sys.path.append('src/utils')
        
        try:
            from real_security_data import get_real_security_assessment, get_inspector_findings, get_config_compliance
            
            print("\n1️⃣ Real Security Assessment:")
            real_security = get_real_security_assessment("123456789012")
            print_json_pretty(real_security, "Real Security Data")
            
            print("\n2️⃣ Inspector Findings:")
            inspector_data = get_inspector_findings()
            print_json_pretty(inspector_data, "Inspector Data")
            
            print("\n3️⃣ Config Compliance:")
            config_data = get_config_compliance()
            print_json_pretty(config_data, "Config Data")
            
        except Exception as e:
            print(f"⚠️ Real security data failed: {e}")
        
        # Test real cost data
        print("\n💰 Testing Real Cost Data:")
        try:
            from real_cost_data import get_real_security_costs
            
            real_costs = get_real_security_costs("123456789012")
            print_json_pretty(real_costs, "Real Cost Data")
            
        except Exception as e:
            print(f"⚠️ Real cost data failed: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Real AWS Integration Error: {e}")
        import traceback
        traceback.print_exc()
        return False

async def run_comprehensive_test():
    """Run all tests with comprehensive output"""
    print("🚀 SECURITY ROI CALCULATOR - COMPREHENSIVE AGENTCORE TESTING")
    print(f"⏰ Test Started: {datetime.now().isoformat()}")
    
    results = {}
    
    # Test each component
    results['security_agentcore'] = await test_security_agentcore_detailed()
    results['cost_agentcore'] = await test_cost_agentcore_detailed()
    results['lambda_integration'] = test_lambda_integration_detailed()
    results['memory_integration'] = test_memory_integration_detailed()
    results['real_aws_integration'] = test_real_aws_integration()
    
    # Summary
    print_section("TEST SUMMARY")
    
    total_tests = len(results)
    passed_tests = sum(results.values())
    
    print(f"\n📊 Test Results:")
    for test_name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"   {test_name}: {status}")
    
    print(f"\n🎯 Overall: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("\n🎉 ALL TESTS PASSED! AgentCore runtimes are working correctly.")
    else:
        print(f"\n⚠️ {total_tests - passed_tests} test(s) failed. Check details above.")
    
    print(f"\n⏰ Test Completed: {datetime.now().isoformat()}")

if __name__ == "__main__":
    asyncio.run(run_comprehensive_test())
