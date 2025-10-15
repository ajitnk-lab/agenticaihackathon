#!/usr/bin/env python3
"""Test Real Memory Storage Once Active"""

import os
import sys
import time
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def check_memory_status():
    """Check if memory is ready"""
    from bedrock_agentcore.memory import MemoryClient
    
    memory_id = os.getenv('SECURITY_MEMORY_ID')
    if not memory_id:
        print("❌ SECURITY_MEMORY_ID not set. Run: source scripts/memory_env.sh")
        return False
    
    client = MemoryClient(region_name='us-west-2')
    
    try:
        memories = client.list_memories()
        for memory in memories:
            if memory.get('id') == memory_id:
                status = memory.get('status', 'unknown')
                print(f"Memory Status: {status}")
                return status == 'ACTIVE'
        
        print(f"❌ Memory {memory_id} not found")
        return False
        
    except Exception as e:
        print(f"❌ Error checking memory: {e}")
        return False

def test_real_storage():
    """Test storing real data in AgentCore Memory"""
    
    if not check_memory_status():
        print("⏳ Memory not ready yet. Try again in a few minutes.")
        return False
    
    try:
        from src.agentcore.memory_integration import SecurityMemoryManager
        
        print("🧪 Testing Real Memory Storage...")
        
        manager = SecurityMemoryManager()
        
        # Store real assessment data
        test_assessment = {
            "timestamp": "2025-10-14T16:51:00Z",
            "account_id": "039920874011",
            "security_score": 75,
            "critical_findings": 3,
            "high_findings": 8,
            "compliance_status": "PARTIAL_COMPLIANCE",
            "test_run": True
        }
        
        manager.store_assessment("039920874011", test_assessment)
        print("✅ Successfully stored assessment in AgentCore Memory!")
        
        # Try to retrieve (may take a moment to be available)
        print("🔍 Attempting to retrieve historical data...")
        trends = manager.get_historical_trends("039920874011", months=1)
        print(f"✅ Retrieved {len(trends)} historical data points")
        
        return True
        
    except Exception as e:
        print(f"❌ Storage test failed: {e}")
        return False

def main():
    print("🧠 Real AgentCore Memory Storage Test")
    print("=" * 50)
    
    if test_real_storage():
        print("\n🎉 SUCCESS! Real memory storage is now active!")
        print("   • Historical data will accumulate with each run")
        print("   • Trends will become more accurate over time")
        print("   • Memory primitive is fully functional")
    else:
        print("\n⏳ Memory not ready yet or needs troubleshooting")
        print("   • AgentCore Memory resources are still being created")
        print("   • This usually takes 2-3 minutes")
        print("   • Try running this script again in a few minutes")

if __name__ == "__main__":
    main()
