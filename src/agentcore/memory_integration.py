"""
Minimal AgentCore Memory primitive integration for Security ROI Calculator.
Provides historical data storage and trend analysis capabilities.
"""

import os
import json
from datetime import datetime
from typing import Dict, List, Any, Optional
from bedrock_agentcore.memory import MemoryClient

class SecurityMemoryManager:
    """Manages historical security assessment data using AgentCore Memory primitive."""
    
    def __init__(self, region_name: str = "us-west-2"):
        self.memory_client = MemoryClient(region_name=region_name)
        self.memory_id = os.getenv('SECURITY_MEMORY_ID')
        
    def store_assessment(self, account_id: str, assessment_data: Dict[str, Any]) -> None:
        """Store security assessment results for historical tracking."""
        if not self.memory_id:
            return
            
        # Create event with assessment data
        self.memory_client.create_event(
            memory_id=self.memory_id,
            actor_id=account_id,
            session_id=f"assessment-{datetime.now().strftime('%Y-%m')}",
            messages=[
                (json.dumps(assessment_data), "ASSISTANT")
            ]
        )
    
    def get_historical_trends(self, account_id: str, months: int = 6) -> List[Dict[str, Any]]:
        """Retrieve historical assessment data for trend analysis."""
        if not self.memory_id:
            return []
            
        # Retrieve memories from semantic namespace
        memories = self.memory_client.retrieve_memories(
            memory_id=self.memory_id,
            namespace=f"security/assessments/{account_id}",
            query="security assessment findings compliance score",
            top_k=months
        )
        
        return [json.loads(memory.get('content', '{}')) for memory in memories]

class CostMemoryManager:
    """Manages historical cost data using AgentCore Memory primitive."""
    
    def __init__(self, region_name: str = "us-west-2"):
        self.memory_client = MemoryClient(region_name=region_name)
        self.memory_id = os.getenv('COST_MEMORY_ID')
        
    def store_cost_analysis(self, account_id: str, cost_data: Dict[str, Any]) -> None:
        """Store cost analysis results for ROI tracking."""
        if not self.memory_id:
            return
            
        self.memory_client.create_event(
            memory_id=self.memory_id,
            actor_id=account_id,
            session_id=f"cost-analysis-{datetime.now().strftime('%Y-%m')}",
            messages=[
                (json.dumps(cost_data), "ASSISTANT")
            ]
        )
    
    def get_roi_trends(self, account_id: str) -> Dict[str, Any]:
        """Calculate ROI trends from historical cost data."""
        if not self.memory_id:
            return {"trend": "No historical data available"}
            
        memories = self.memory_client.retrieve_memories(
            memory_id=self.memory_id,
            namespace=f"costs/analysis/{account_id}",
            query="security spending ROI cost analysis",
            top_k=12
        )
        
        if len(memories) < 2:
            return {"trend": "Insufficient data for trend analysis"}
            
        # Simple trend calculation
        recent_roi = float(memories[0].get('roi_percentage', 0))
        older_roi = float(memories[-1].get('roi_percentage', 0))
        trend_direction = "improving" if recent_roi > older_roi else "declining"
        
        return {
            "trend": trend_direction,
            "current_roi": recent_roi,
            "historical_roi": older_roi,
            "data_points": len(memories)
        }

def setup_memory_resources():
    """Setup memory resources for Security ROI Calculator (run once)."""
    client = MemoryClient(region_name='us-west-2')
    
    # Create security assessment memory with semantic extraction
    security_memory = client.create_memory_and_wait(
        name=f"SecurityROI_Assessments",
        strategies=[
            {
                "semanticMemoryStrategy": {
                    "name": "security_facts",
                    "namespaces": ["security/assessments/{actorId}"]
                }
            }
        ],
        event_expiry_days=365
    )
    
    # Create cost analysis memory
    cost_memory = client.create_memory_and_wait(
        name=f"SecurityROI_Costs",
        strategies=[
            {
                "semanticMemoryStrategy": {
                    "name": "cost_trends",
                    "namespaces": ["costs/analysis/{actorId}"]
                }
            }
        ],
        event_expiry_days=365
    )
    
    print(f"Security Memory ID: {security_memory['id']}")
    print(f"Cost Memory ID: {cost_memory['id']}")
    print("\nSet environment variables:")
    print(f"export SECURITY_MEMORY_ID={security_memory['id']}")
    print(f"export COST_MEMORY_ID={cost_memory['id']}")
    
    return security_memory['id'], cost_memory['id']

if __name__ == "__main__":
    setup_memory_resources()
