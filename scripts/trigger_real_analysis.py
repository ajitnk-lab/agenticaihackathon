#!/usr/bin/env python3
"""
Trigger Real Security Analysis and Store in Memory
This script pulls real data from AWS services and stores it in AgentCore Memory
"""

import asyncio
import json
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

async def trigger_security_analysis():
    """Trigger security analysis with real data"""
    print("🔍 Triggering Real Security Analysis...")
    
    # Import AgentCore runtime
    from src.agentcore.well_architected_security_agentcore import handler
    
    # Trigger security analysis
    event = {'prompt': 'analyze_security_posture for account 039920874011'}
    result = await handler(event)
    
    security_data = json.loads(result['body'])
    print("✅ Security Analysis Complete:")
    print(f"   Security Score: {security_data.get('security_score', 'unknown')}")
    print(f"   Data Source: {security_data.get('data_source', 'unknown')}")
    print(f"   Compliance: {security_data.get('compliance_status', 'unknown')}")
    
    return security_data

async def trigger_cost_analysis():
    """Trigger cost analysis"""
    print("\n💰 Triggering Cost Analysis...")
    
    from src.agentcore.cost_analysis_agentcore import handler
    
    event = {'prompt': 'get_security_costs for account 039920874011'}
    result = await handler(event)
    
    cost_data = json.loads(result['body'])
    print("✅ Cost Analysis Complete:")
    print(f"   Total Cost: ${cost_data.get('total_security_cost', 'unknown')}")
    
    return cost_data

async def trigger_historical_trends():
    """Get historical trends from Memory"""
    print("\n🧠 Retrieving Historical Trends from Memory...")
    
    from src.agentcore.cost_analysis_agentcore import handler
    
    event = {'prompt': 'roi_trends for account 039920874011'}
    result = await handler(event)
    
    trends_data = json.loads(result['body'])
    print("✅ Historical Trends Retrieved:")
    print(f"   Trend: {trends_data.get('historical_analysis', {}).get('trend', 'unknown')}")
    print(f"   Data Points: {trends_data.get('historical_analysis', {}).get('data_points', 0)}")
    
    return trends_data

async def main():
    """Run complete real data analysis and storage"""
    print("🚀 Real Security Analysis with AgentCore Memory Storage")
    print("=" * 60)
    
    # Check memory environment
    if not os.getenv('SECURITY_MEMORY_ID'):
        print("❌ Memory not configured. Run: source scripts/memory_env.sh")
        return
    
    print(f"🧠 Memory ID: {os.getenv('SECURITY_MEMORY_ID')}")
    
    # Run all analyses
    security_data = await trigger_security_analysis()
    cost_data = await trigger_cost_analysis()
    trends_data = await trigger_historical_trends()
    
    print(f"\n🎯 Summary:")
    print(f"   ✅ Real security data collected and stored in Memory")
    print(f"   ✅ Cost analysis completed")
    print(f"   ✅ Historical trends retrieved from Memory")
    print(f"   ✅ All data available for executive reporting")
    
    # Show executive summary
    print(f"\n📊 Executive Summary:")
    print(f"   Security Score: {security_data.get('security_score', 'N/A')}/100")
    print(f"   Monthly Security Cost: ${cost_data.get('total_security_cost', 'N/A')}")
    print(f"   ROI Trend: {trends_data.get('historical_analysis', {}).get('trend', 'N/A')}")
    print(f"   Data Source: {security_data.get('data_source', 'N/A')}")

if __name__ == "__main__":
    asyncio.run(main())
