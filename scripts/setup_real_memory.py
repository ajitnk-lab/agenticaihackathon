#!/usr/bin/env python3
"""
Setup Real AgentCore Memory Resources
Run this once to enable actual historical data storage
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def setup_real_memory():
    """Setup actual AgentCore Memory resources"""
    
    print("🧠 Setting up Real AgentCore Memory Resources...")
    
    try:
        from src.agentcore.memory_integration import setup_memory_resources
        
        # Create memory resources
        security_id, cost_id = setup_memory_resources()
        
        # Create environment file
        env_content = f"""# AgentCore Memory Environment Variables
export SECURITY_MEMORY_ID={security_id}
export COST_MEMORY_ID={cost_id}

# Usage: source this file before running tests
# source scripts/memory_env.sh
"""
        
        with open('scripts/memory_env.sh', 'w') as f:
            f.write(env_content)
        
        print(f"✅ Memory Resources Created!")
        print(f"   Security Memory ID: {security_id}")
        print(f"   Cost Memory ID: {cost_id}")
        print(f"")
        print(f"🔧 To enable real memory storage:")
        print(f"   source scripts/memory_env.sh")
        print(f"   python3 tests/interactive_memory_demo.py")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to setup memory: {e}")
        print(f"")
        print(f"💡 This requires:")
        print(f"   - AWS credentials configured")
        print(f"   - AgentCore Memory service access")
        print(f"   - Proper IAM permissions")
        return False

def test_memory_storage():
    """Test if memory storage is working"""
    
    if not os.getenv('SECURITY_MEMORY_ID'):
        print("❌ Memory not configured. Run setup first.")
        return False
    
    try:
        from src.agentcore.memory_integration import SecurityMemoryManager
        
        manager = SecurityMemoryManager()
        
        # Try to store test data
        test_data = {
            "timestamp": "2025-10-14T16:47:59Z",
            "security_score": 75,
            "test": True
        }
        
        manager.store_assessment("test-account", test_data)
        print("✅ Memory storage test successful!")
        return True
        
    except Exception as e:
        print(f"❌ Memory storage test failed: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        test_memory_storage()
    else:
        setup_real_memory()
