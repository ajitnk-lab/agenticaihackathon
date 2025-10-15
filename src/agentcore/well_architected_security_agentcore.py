#!/usr/bin/env python3
from bedrock_agentcore.runtime import BedrockAgentCoreApp
import json
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.real_security_data import get_real_security_assessment

# Import memory integration
try:
    from .memory_integration import SecurityMemoryManager
except ImportError:
    from memory_integration import SecurityMemoryManager

app = BedrockAgentCoreApp()
memory_manager = SecurityMemoryManager()

def analyze_security_posture(account_id: str = "123456789012"):
    """Analyze AWS account security posture using REAL data"""
    try:
        # Get REAL security assessment
        real_data = get_real_security_assessment(account_id)
        memory_manager.store_assessment(account_id, real_data)
        return real_data
    except Exception as e:
        # Fallback to mock data if AWS calls fail
        return {
            "account_id": account_id,
            "security_score": 85,
            "error": f"Using mock data: {str(e)}"
        }

def get_security_findings(account_id: str = "123456789012"):
    """Get REAL security findings"""
    try:
        from utils.real_security_data import get_inspector_findings
        findings = get_inspector_findings()
        memory_manager.store_assessment(account_id, findings)
        return findings
    except Exception as e:
        return {"account_id": account_id, "findings_count": 12, "error": f"Using mock data: {str(e)}"}

@app.entrypoint
async def handler(event):
    """AgentCore entrypoint"""
    try:
        prompt = event.get("prompt", "")
        
        if "analyze_security_posture" in prompt.lower():
            result = analyze_security_posture()
        elif "get_security_findings" in prompt.lower():
            result = get_security_findings()
        else:
            result = {"available_tools": ["analyze_security_posture", "get_security_findings"]}
        
        return {"body": json.dumps(result, indent=2)}
    except Exception as e:
        return {"body": json.dumps({"error": str(e)})}

if __name__ == "__main__":
    app.run()
