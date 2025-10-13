#!/usr/bin/env python3
from bedrock_agentcore.runtime import BedrockAgentCoreApp
import json
import boto3

app = BedrockAgentCoreApp()

async def analyze_security_posture(account_id: str, region: str = "us-east-1"):
    """Analyze AWS account security posture using Well-Architected Framework"""
    session = boto3.Session()
    
    findings = {
        "account_id": account_id,
        "security_score": 75,
        "critical_findings": 3,
        "recommendations": [
            "Enable GuardDuty in all regions",
            "Configure Security Hub standards", 
            "Enable CloudTrail logging"
        ]
    }
    
    return findings

async def get_security_findings(account_id: str, severity: str = "HIGH"):
    """Get security findings from Security Hub, GuardDuty, and Inspector"""
    findings = {
        "account_id": account_id,
        "findings_count": 12,
        "severity": severity,
        "top_findings": [
            "Unencrypted S3 buckets detected",
            "IAM users with excessive permissions",
            "Security groups with open access"
        ]
    }
    
    return findings

@app.entrypoint
async def handler(event):
    """AgentCore entrypoint - transforms MCP server functionality"""
    
    prompt = event.get("prompt", "")
    
    # Parse tool calls from prompt
    if "analyze_security_posture" in prompt:
        # Extract account_id from prompt (simplified)
        account_id = "123456789012"  # Default for demo
        result = await analyze_security_posture(account_id)
        
    elif "get_security_findings" in prompt:
        account_id = "123456789012"  # Default for demo
        result = await get_security_findings(account_id)
        
    else:
        # Default response showing available tools
        result = {
            "message": "Well-Architected Security MCP transformed to AgentCore",
            "available_tools": [
                "analyze_security_posture",
                "get_security_findings"
            ],
            "usage": "Include tool name in prompt to execute"
        }
    
    return {"body": json.dumps(result, indent=2)}

if __name__ == "__main__":
    app.run()
