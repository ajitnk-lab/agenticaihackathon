#!/usr/bin/env python3
"""Setup AgentCore Memory resources for Security ROI Calculator"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.agentcore.memory_integration import setup_memory_resources

def main():
    """Setup Memory primitive resources"""
    print("🧠 Setting up AgentCore Memory Primitive...")
    
    try:
        security_id, cost_id = setup_memory_resources()
        
        # Create environment file
        env_content = f"""# AgentCore Memory Configuration
export SECURITY_MEMORY_ID={security_id}
export COST_MEMORY_ID={cost_id}
export AWS_DEFAULT_REGION=us-west-2
"""
        
        with open('.env.memory', 'w') as f:
            f.write(env_content)
        
        print("✅ Memory resources created successfully!")
        print("✅ Environment file created: .env.memory")
        print("\nTo use: source .env.memory")
        
    except Exception as e:
        print(f"❌ Memory setup failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
