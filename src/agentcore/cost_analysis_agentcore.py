#!/usr/bin/env python3
from bedrock_agentcore.runtime import BedrockAgentCoreApp
import json
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.real_cost_data import get_real_security_costs

# Import memory integration
try:
    from .memory_integration import CostMemoryManager
except ImportError:
    from memory_integration import CostMemoryManager

app = BedrockAgentCoreApp()
memory_manager = CostMemoryManager()

def get_security_costs(account_id: str = "123456789012"):
    """Get REAL security service costs from Cost Explorer"""
    try:
        real_costs = get_real_security_costs(account_id)
        return real_costs
    except Exception as e:
        # Fallback to mock data if AWS calls fail
        return {
            "account_id": account_id,
            "total_security_cost": 1250.75,
            "error": f"Using mock data: {str(e)}"
        }

def calculate_security_roi(account_id: str = "123456789012"):
    """Calculate ROI using REAL cost data"""
    try:
        costs = get_security_costs(account_id)
        annual_cost = costs.get("total_security_cost", 1250.75) * 12
        potential_savings = annual_cost * 3.5  # Industry average ROI
        
        roi_result = {
            "account_id": account_id,
            "annual_investment": annual_cost,
            "potential_savings": potential_savings,
            "roi_percentage": round(((potential_savings - annual_cost) / annual_cost) * 100, 1),
            "data_source": "real_aws_costs" if "error" not in costs else "mock_data"
        }
        
        memory_manager.store_cost_analysis(account_id, roi_result)
        return roi_result
    except Exception as e:
        return {"account_id": account_id, "error": str(e)}

def get_roi_trends(account_id: str = "123456789012"):
    """Get ROI trends from Memory primitive"""
    trends = memory_manager.get_roi_trends(account_id)
    return {"historical_analysis": trends}

@app.entrypoint
async def handler(event):
    """AgentCore entrypoint"""
    try:
        prompt = event.get("prompt", "")
        
        if "get_security_costs" in prompt.lower():
            result = get_security_costs()
        elif "calculate_security_roi" in prompt.lower():
            result = calculate_security_roi()
        elif "roi_trends" in prompt.lower():
            result = get_roi_trends()
        else:
            result = {"available_tools": ["get_security_costs", "calculate_security_roi", "get_roi_trends"]}
        
        return {"body": json.dumps(result, indent=2)}
    except Exception as e:
        return {"body": json.dumps({"error": str(e)})}

if __name__ == "__main__":
    app.run()
