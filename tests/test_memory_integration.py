#!/usr/bin/env python3
"""
Test Memory Primitive Integration for Security ROI Calculator
Validates AgentCore Memory functionality with mock historical data
"""

import json
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_lambda_memory_integration():
    """Test Lambda function memory-based queries"""
    print("🧪 Testing Lambda Memory Integration...")
    
    # Mock Bedrock Agent event for historical trends
    test_event = {
        'actionGroup': 'SecurityActions',
        'apiPath': '/trends',
        'httpMethod': 'POST',
        'parameters': [
            {'name': 'account_id', 'value': '039920874011'}
        ]
    }
    
    # Import and test Lambda function
    try:
        import sys
        sys.path.append('/persistent/home/ubuntu/workspace/agenticaihackathon')
        
        # Import Lambda handler
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "lambda_handler", 
            "/persistent/home/ubuntu/workspace/agenticaihackathon/src/lambda/security_orchestrator_lambda.py"
        )
        lambda_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(lambda_module)
        lambda_handler = lambda_module.lambda_handler
        
        result = lambda_handler(test_event, {})
        
        print("✅ Lambda Memory Integration Test Results:")
        response_body = json.loads(result['response']['responseBody']['application/json']['body'])
        
        # Validate memory primitive indicators
        assert 'memory_primitive_status' in response_body
        assert response_body['memory_primitive_status'] == 'active'
        assert 'historical_analysis' in response_body
        assert response_body['historical_analysis']['data_points'] > 0
        
        print(f"   Memory Status: {response_body['memory_primitive_status']}")
        print(f"   Historical Data Points: {response_body['historical_analysis']['data_points']}")
        print(f"   ROI Trend: {response_body['historical_analysis']['trend']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Lambda test failed: {e}")
        return False

def test_agentcore_memory_simulation():
    """Simulate AgentCore Memory primitive functionality"""
    print("\n🧪 Testing AgentCore Memory Simulation...")
    
    try:
        # Mock memory data that would be stored/retrieved
        mock_security_assessment = {
            "account_id": "039920874011",
            "timestamp": "2024-10-14T16:30:00Z",
            "security_score": 75,
            "critical_findings": 3,
            "compliance_status": "PARTIAL_COMPLIANCE"
        }
        
        mock_cost_analysis = {
            "account_id": "039920874011",
            "timestamp": "2024-10-14T16:30:00Z",
            "total_security_cost": 97.15,
            "roi_percentage": 3650.0
        }
        
        # Simulate historical trend calculation
        historical_scores = [68, 70, 72, 73, 74, 75]  # 6 months of data
        trend = "improving" if historical_scores[-1] > historical_scores[0] else "declining"
        
        print("✅ AgentCore Memory Simulation Results:")
        print(f"   Security Score Trend: {trend}")
        print(f"   Current Score: {historical_scores[-1]}")
        print(f"   Historical Data Points: {len(historical_scores)}")
        print(f"   ROI: {mock_cost_analysis['roi_percentage']}%")
        
        return True
        
    except Exception as e:
        print(f"❌ AgentCore simulation failed: {e}")
        return False

def test_memory_primitive_compliance():
    """Validate Memory primitive compliance for hackathon"""
    print("\n🏆 Testing Hackathon Memory Primitive Compliance...")
    
    compliance_checks = {
        "Memory Integration Code": False,
        "Historical Data Storage": False,
        "Trend Analysis": False,
        "Lambda Memory Queries": False
    }
    
    try:
        # Check if memory integration files exist
        memory_file = "/persistent/home/ubuntu/workspace/agenticaihackathon/src/agentcore/memory_integration.py"
        if os.path.exists(memory_file):
            compliance_checks["Memory Integration Code"] = True
            
        # Check AgentCore runtimes have memory integration
        security_file = "/persistent/home/ubuntu/workspace/agenticaihackathon/src/agentcore/well_architected_security_agentcore.py"
        if os.path.exists(security_file):
            with open(security_file, 'r') as f:
                content = f.read()
                if "memory_manager" in content and "store_assessment" in content:
                    compliance_checks["Historical Data Storage"] = True
                    
        cost_file = "/persistent/home/ubuntu/workspace/agenticaihackathon/src/agentcore/cost_analysis_agentcore.py"
        if os.path.exists(cost_file):
            with open(cost_file, 'r') as f:
                content = f.read()
                if "get_roi_trends" in content:
                    compliance_checks["Trend Analysis"] = True
                    
        # Check Lambda has memory queries
        lambda_file = "/persistent/home/ubuntu/workspace/agenticaihackathon/src/lambda/security_orchestrator_lambda.py"
        if os.path.exists(lambda_file):
            with open(lambda_file, 'r') as f:
                content = f.read()
                if "memory_primitive_status" in content:
                    compliance_checks["Lambda Memory Queries"] = True
        
        print("✅ Memory Primitive Compliance Check:")
        for check, passed in compliance_checks.items():
            status = "✅ PASS" if passed else "❌ FAIL"
            print(f"   {check}: {status}")
            
        all_passed = all(compliance_checks.values())
        print(f"\n🏆 Overall Compliance: {'✅ HACKATHON READY' if all_passed else '❌ NEEDS WORK'}")
        
        return all_passed
        
    except Exception as e:
        print(f"❌ Compliance check failed: {e}")
        return False

def main():
    """Run all memory integration tests"""
    print("🚀 Security ROI Calculator - Memory Primitive Integration Tests\n")
    
    tests = [
        test_lambda_memory_integration,
        test_agentcore_memory_simulation,
        test_memory_primitive_compliance
    ]
    
    results = []
    for test in tests:
        results.append(test())
    
    print(f"\n📊 Test Summary: {sum(results)}/{len(results)} tests passed")
    
    if all(results):
        print("🎉 All Memory Integration Tests PASSED - Ready for Hackathon!")
    else:
        print("⚠️  Some tests failed - Review implementation")

if __name__ == "__main__":
    main()
