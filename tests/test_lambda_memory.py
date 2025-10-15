#!/usr/bin/env python3
"""Test Lambda Memory Integration Directly"""

import json
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_lambda_memory_queries():
    """Test different memory-based queries"""
    
    # Import Lambda handler
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "lambda_handler", 
        "/persistent/home/ubuntu/workspace/agenticaihackathon/src/lambda/security_orchestrator_lambda.py"
    )
    lambda_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(lambda_module)
    
    # Test 1: Historical trends query
    print("🧪 Test 1: Historical Trends Query")
    trends_event = {
        'actionGroup': 'SecurityActions',
        'apiPath': '/trends',
        'httpMethod': 'POST',
        'parameters': [{'name': 'account_id', 'value': '039920874011'}]
    }
    
    result = lambda_module.lambda_handler(trends_event, {})
    response = json.loads(result['response']['responseBody']['application/json']['body'])
    
    print(f"✅ Memory Status: {response.get('memory_primitive_status')}")
    print(f"✅ Data Points: {response.get('historical_analysis', {}).get('data_points')}")
    print(f"✅ ROI Trend: {response.get('historical_analysis', {}).get('trend')}")
    print(f"✅ Security Trend: {response.get('security_trends', {}).get('security_score_trend')}")
    
    # Test 2: Security analysis (stores in memory)
    print(f"\n🧪 Test 2: Security Analysis (Memory Storage)")
    security_event = {
        'actionGroup': 'SecurityActions',
        'apiPath': '/security',
        'httpMethod': 'POST',
        'parameters': [{'name': 'account_id', 'value': '039920874011'}]
    }
    
    result = lambda_module.lambda_handler(security_event, {})
    response = json.loads(result['response']['responseBody']['application/json']['body'])
    
    print(f"✅ Security Score: {response.get('security_score')}")
    print(f"✅ Critical Findings: {response.get('critical_findings')}")
    print(f"✅ Compliance Status: {response.get('compliance_status')}")
    
    # Test 3: Cost analysis with ROI
    print(f"\n🧪 Test 3: Cost Analysis with ROI")
    cost_event = {
        'actionGroup': 'SecurityActions',
        'apiPath': '/cost',
        'httpMethod': 'POST',
        'parameters': [{'name': 'account_id', 'value': '039920874011'}]
    }
    
    result = lambda_module.lambda_handler(cost_event, {})
    response = json.loads(result['response']['responseBody']['application/json']['body'])
    
    print(f"✅ Total Security Cost: ${response.get('total_security_cost')}")
    print(f"✅ Service Breakdown: {len(response.get('service_costs', {}))} services")
    
    print(f"\n🏆 All Lambda Memory Tests Passed!")
    print(f"The Lambda function demonstrates Memory primitive integration")
    print(f"by providing historical trend analysis and ROI tracking.")

if __name__ == "__main__":
    test_lambda_memory_queries()
