#!/usr/bin/env python3
"""Test individual AgentCore runtimes"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import asyncio
import json

def test_security_runtime():
    """Test Security AgentCore runtime"""
    print("Testing Security AgentCore Runtime...")
    
    try:
        from src.agentcore.well_architected_security_agentcore import handler
        
        # Test analyze_security_posture
        event = {"prompt": "analyze_security_posture"}
        result = asyncio.run(handler(event))
        print("✅ Security posture analysis:", json.loads(result["body"])["security_score"])
        
        # Test get_security_findings
        event = {"prompt": "get_security_findings"}
        result = asyncio.run(handler(event))
        print("✅ Security findings:", json.loads(result["body"])["findings_count"])
        
        return True
    except Exception as e:
        print(f"❌ Security runtime error: {e}")
        return False

def test_cost_runtime():
    """Test Cost Analysis AgentCore runtime"""
    print("\nTesting Cost Analysis AgentCore Runtime...")
    
    try:
        from src.agentcore.cost_analysis_agentcore import handler
        
        # Test get_security_costs
        event = {"prompt": "get_security_costs"}
        result = asyncio.run(handler(event))
        print("✅ Security costs:", json.loads(result["body"])["total_security_cost"])
        
        # Test calculate_security_roi
        event = {"prompt": "calculate_security_roi"}
        result = asyncio.run(handler(event))
        print("✅ ROI calculation:", json.loads(result["body"])["roi_percentage"])
        
        return True
    except Exception as e:
        print(f"❌ Cost runtime error: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing AgentCore Runtimes Individually\n")
    
    security_ok = test_security_runtime()
    cost_ok = test_cost_runtime()
    
    if security_ok and cost_ok:
        print("\n✅ All AgentCore runtimes working correctly!")
    else:
        print("\n❌ Some runtimes have issues")
        sys.exit(1)
