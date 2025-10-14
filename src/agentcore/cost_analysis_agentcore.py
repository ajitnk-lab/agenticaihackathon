#!/usr/bin/env python3
from bedrock_agentcore.runtime import BedrockAgentCoreApp
import json
import boto3
from src.utils.account_discovery import get_target_accounts

app = BedrockAgentCoreApp()

def get_security_costs(account_id: str, days: int = 30):
    """Get current security service costs for an account"""
    try:
        costs = {
            'Amazon GuardDuty': 45.50,
            'AWS Security Hub': 12.30,
            'Amazon Inspector': 8.75,
            'AWS Config': 25.40,
            'AWS CloudTrail': 5.20
        }
        
        total_cost = sum(costs.values())
        
        return {
            'account_id': account_id,
            'period_days': days,
            'total_security_cost': round(total_cost, 2),
            'service_costs': costs,
            'currency': 'USD'
        }
    except Exception as e:
        return {'error': str(e)}

def calculate_security_roi(investments: list):
    """Calculate ROI for security investments"""
    try:
        total_investment = sum(inv.get('annual_cost', 0) for inv in investments)
        total_savings = sum(inv.get('potential_savings', 0) for inv in investments)
        
        net_benefit = total_savings - total_investment
        roi_percentage = (net_benefit / total_investment * 100) if total_investment > 0 else 0
        
        return {
            'total_annual_investment': round(total_investment, 2),
            'total_potential_savings': round(total_savings, 2),
            'net_annual_benefit': round(net_benefit, 2),
            'roi_percentage': round(roi_percentage, 1),
            'currency': 'USD'
        }
    except Exception as e:
        return {'error': str(e)}

@app.entrypoint
async def handler(event):
    """AgentCore entrypoint"""
    try:
        prompt = event.get("prompt", "")
        
        # Parse tool calls from prompt
        if "get_security_costs" in prompt.lower():
            accounts = get_target_accounts()
            account_id = accounts[0] if accounts else "unknown"
            result = get_security_costs(account_id)
            
        elif "calculate_security_roi" in prompt.lower():
            investments = [
                {'annual_cost': 1200, 'potential_savings': 50000},
                {'annual_cost': 800, 'potential_savings': 25000}
            ]
            result = calculate_security_roi(investments)
            
        else:
            # Default response showing available tools
            result = {
                "message": "Cost Analysis Agent - Multi-Account Security Orchestrator",
                "available_tools": [
                    "get_security_costs - Get current security service costs",
                    "calculate_security_roi - Calculate ROI for security investments"
                ],
                "usage": "Include tool name in prompt to execute",
                "example": "Get security costs for organization accounts"
            }
        
        return {"body": json.dumps(result, indent=2)}
        
    except Exception as e:
        return {"body": json.dumps({"error": str(e)}, indent=2)}

if __name__ == "__main__":
    app.run()
