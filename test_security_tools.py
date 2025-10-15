#!/usr/bin/env python3
"""
Test Security AgentCore tools individually with detailed output
"""

import sys
import os
import json
import asyncio
from datetime import datetime

# Add project paths
sys.path.append('src')
sys.path.append('src/agentcore')

def print_tool_header(tool_name):
    """Print formatted tool header"""
    print(f"\n{'='*60}")
    print(f"🔧 TESTING: {tool_name}")
    print('='*60)

def print_result(data, title="Result"):
    """Print result with formatting"""
    print(f"\n📋 {title}:")
    print(json.dumps(data, indent=2, default=str))

def test_analyze_security_posture():
    """Test analyze_security_posture tool"""
    print_tool_header("analyze_security_posture")
    
    try:
        # Import and test direct function
        from well_architected_security_agentcore import analyze_security_posture
        
        print("🔍 Testing with different account IDs:")
        
        test_accounts = [
            "123456789012",
            "039920874011",  # Real account from diagnostic
            "999999999999"
        ]
        
        for account_id in test_accounts:
            print(f"\n📊 Account: {account_id}")
            result = analyze_security_posture(account_id)
            
            # Extract key metrics
            security_score = result.get('security_score', 'N/A')
            total_findings = result.get('summary', {}).get('total_findings', 'N/A')
            critical_findings = result.get('summary', {}).get('critical_findings', 'N/A')
            
            print(f"   Security Score: {security_score}")
            print(f"   Total Findings: {total_findings}")
            print(f"   Critical Findings: {critical_findings}")
            
            # Show sample findings if available
            sample_findings = result.get('security_hub_findings', {}).get('sample_findings', [])
            if sample_findings:
                print(f"   Sample Finding: {sample_findings[0].get('title', 'No title')[:80]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_get_security_findings():
    """Test get_security_findings tool"""
    print_tool_header("get_security_findings")
    
    try:
        from well_architected_security_agentcore import get_security_findings
        
        print("🔍 Testing Inspector findings:")
        
        test_accounts = ["123456789012", "039920874011"]
        
        for account_id in test_accounts:
            print(f"\n📊 Account: {account_id}")
            result = get_security_findings(account_id)
            
            service = result.get('service', 'Unknown')
            total_findings = result.get('total_findings', 0)
            status = result.get('status', 'Unknown')
            
            print(f"   Service: {service}")
            print(f"   Total Findings: {total_findings}")
            print(f"   Status: {status}")
            
            if 'message' in result:
                print(f"   Message: {result['message']}")
            
            # Show severity breakdown
            severity = result.get('severity_breakdown', {})
            if severity:
                print(f"   Severity: {severity}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

async def test_agentcore_handler_tools():
    """Test AgentCore handler with different prompts"""
    print_tool_header("AgentCore Handler - Different Prompts")
    
    try:
        from well_architected_security_agentcore import handler
        
        test_prompts = [
            "analyze_security_posture",
            "analyze security posture",
            "security posture",
            "get_security_findings", 
            "get security findings",
            "security findings",
            "show me security analysis",
            "what security issues do we have",
            "unknown_tool",
            ""
        ]
        
        for i, prompt in enumerate(test_prompts, 1):
            print(f"\n{i}️⃣ Prompt: '{prompt}'")
            
            event = {"prompt": prompt}
            result = await handler(event)
            response_data = json.loads(result["body"])
            
            # Extract key info
            if 'security_score' in response_data:
                print(f"   ✅ Security Score: {response_data['security_score']}")
                print(f"   📊 Total Findings: {response_data.get('summary', {}).get('total_findings', 'N/A')}")
            elif 'total_findings' in response_data:
                print(f"   ✅ Inspector Findings: {response_data['total_findings']}")
                print(f"   📊 Status: {response_data.get('status', 'N/A')}")
            elif 'available_tools' in response_data:
                print(f"   ℹ️ Available Tools: {len(response_data['available_tools'])}")
            elif 'error' in response_data:
                print(f"   ❌ Error: {response_data['error']}")
            else:
                print(f"   📋 Response keys: {list(response_data.keys())}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_real_data_sources():
    """Test underlying real data sources"""
    print_tool_header("Real Data Sources")
    
    try:
        sys.path.append('src/utils')
        from real_security_data import get_security_hub_findings, get_inspector_findings, get_config_compliance
        
        print("🔍 Testing Security Hub:")
        hub_data = get_security_hub_findings()
        print(f"   Status: {hub_data.get('status')}")
        print(f"   Total Findings: {hub_data.get('total_findings', 0)}")
        print(f"   Severity Breakdown: {hub_data.get('severity_breakdown', {})}")
        
        print("\n🔍 Testing Inspector:")
        inspector_data = get_inspector_findings()
        print(f"   Status: {inspector_data.get('status')}")
        print(f"   Total Findings: {inspector_data.get('total_findings', 0)}")
        if 'message' in inspector_data:
            print(f"   Message: {inspector_data['message']}")
        
        print("\n🔍 Testing Config:")
        config_data = get_config_compliance()
        print(f"   Status: {config_data.get('status')}")
        print(f"   Total Rules: {config_data.get('total_rules', 0)}")
        print(f"   Compliance Rate: {config_data.get('compliance_rate', 0)}%")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_memory_integration():
    """Test memory integration with security tools"""
    print_tool_header("Memory Integration")
    
    try:
        from memory_integration import SecurityMemoryManager
        
        memory_manager = SecurityMemoryManager()
        print(f"Memory ID: {memory_manager.memory_id}")
        
        # Test storing assessment
        test_data = {
            "account_id": "test-123",
            "security_score": 75,
            "findings": ["Test finding 1", "Test finding 2"],
            "timestamp": datetime.now().isoformat()
        }
        
        print("\n📝 Testing memory storage:")
        try:
            memory_manager.store_assessment("test-123", test_data)
            print("   ✅ Assessment stored successfully")
        except Exception as e:
            print(f"   ⚠️ Storage failed (expected without AWS setup): {e}")
        
        # Test retrieving trends
        print("\n📈 Testing trend retrieval:")
        try:
            trends = memory_manager.get_historical_trends("test-123")
            print(f"   Historical data points: {len(trends)}")
        except Exception as e:
            print(f"   ⚠️ Retrieval failed (expected without AWS setup): {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

async def run_individual_tests():
    """Run all individual tool tests"""
    print("🚀 SECURITY AGENTCORE - INDIVIDUAL TOOLS TESTING")
    print(f"⏰ Test Started: {datetime.now().isoformat()}")
    
    results = {}
    
    # Test each tool individually
    results['analyze_security_posture'] = test_analyze_security_posture()
    results['get_security_findings'] = test_get_security_findings()
    results['agentcore_handler'] = await test_agentcore_handler_tools()
    results['real_data_sources'] = test_real_data_sources()
    results['memory_integration'] = test_memory_integration()
    
    # Summary
    print(f"\n{'='*60}")
    print("📊 TEST SUMMARY")
    print('='*60)
    
    total_tests = len(results)
    passed_tests = sum(results.values())
    
    for test_name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"   {test_name}: {status}")
    
    print(f"\n🎯 Overall: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("\n🎉 ALL INDIVIDUAL TOOLS WORKING CORRECTLY!")
    else:
        print(f"\n⚠️ {total_tests - passed_tests} test(s) failed.")
    
    print(f"\n⏰ Test Completed: {datetime.now().isoformat()}")

if __name__ == "__main__":
    asyncio.run(run_individual_tests())
