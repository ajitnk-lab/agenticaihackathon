#!/usr/bin/env python3
"""
Real Security Analysis AgentCore Runtime
Uses actual Inspector + Config data instead of mock data
"""
from bedrock_agentcore.runtime import BedrockAgentCoreApp
import json
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.utils.real_security_data import get_real_security_assessment
from src.utils.account_discovery import get_target_accounts
from src.agentcore.memory_integration import SecurityMemoryManager

app = BedrockAgentCoreApp()
memory_manager = SecurityMemoryManager()

def analyze_security_posture_real(account_id: str, region: str = "us-east-1"):
    """Analyze AWS account security posture using REAL Inspector + Config data"""
    try:
        # Get real security assessment
        real_assessment = get_real_security_assessment(account_id, region)
        
        # Transform to expected format
        findings = {
            "account_id": account_id,
            "region": region,
            "security_score": real_assessment["security_score"],
            "inspector_findings": real_assessment["inspector_findings"]["total_findings"],
            "config_compliance_rate": real_assessment["config_compliance"]["compliance_rate"],
            "assessment_timestamp": real_assessment["assessment_timestamp"],
            "data_source": "real_aws_services",
            "services_analyzed": ["Amazon Inspector", "AWS Config"],
            "recommendations": []
        }
        
        # Add recommendations based on real data
        if real_assessment["inspector_findings"]["total_findings"] > 0:
            findings["recommendations"].append("Review and remediate Inspector findings")
        
        if real_assessment["config_compliance"]["compliance_rate"] < 100:
            findings["recommendations"].append("Improve Config rule compliance")
            
        if real_assessment["config_compliance"]["total_rules"] == 0:
            findings["recommendations"].append("Enable Config rules for compliance monitoring")
            
        if not findings["recommendations"]:
            findings["recommendations"] = ["Account shows good security posture", "Consider enabling GuardDuty for threat detection"]
        
        # Store REAL assessment in memory for historical tracking
        memory_manager.store_assessment(account_id, findings)
        
        return findings
        
    except Exception as e:
        return {'error': str(e)}

@app.entrypoint
async def handler(event):
    """AgentCore entrypoint for REAL security analysis"""
    try:
        prompt = event.get("prompt", "")
        
        if "analyze_security_posture" in prompt.lower() or "security posture" in prompt.lower():
            accounts = get_target_accounts()
            account_id = accounts[0] if accounts else "039920874011"
            result = analyze_security_posture_real(account_id)
            
        else:
            result = {
                "message": "Real Security Agent - Using Inspector + Config",
                "available_tools": [
                    "analyze_security_posture_real - Real security analysis using Inspector + Config"
                ],
                "data_source": "real_aws_services"
            }
        
        return {"body": json.dumps(result, indent=2, default=str)}
        
    except Exception as e:
        return {"body": json.dumps({"error": str(e)}, indent=2)}

if __name__ == "__main__":
    app.run()
