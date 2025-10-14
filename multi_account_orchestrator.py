#!/usr/bin/env python3
import asyncio
import json
from concurrent.futures import ThreadPoolExecutor
from account_discovery import get_organization_accounts
from well_architected_security_agentcore import analyze_security_posture, get_security_findings
from cost_analysis_agentcore import get_security_costs, calculate_security_roi

async def analyze_all_accounts():
    """Analyze security posture across all organization accounts"""
    accounts = get_organization_accounts()
    
    with ThreadPoolExecutor(max_workers=10) as executor:
        # Analyze security posture for all accounts in parallel
        security_tasks = [
            executor.submit(analyze_security_posture, acc['id']) 
            for acc in accounts
        ]
        
        # Get cost analysis for all accounts in parallel  
        cost_tasks = [
            executor.submit(get_security_costs, acc['id'])
            for acc in accounts
        ]
        
        # Collect results
        security_results = [task.result() for task in security_tasks]
        cost_results = [task.result() for task in cost_tasks]
    
    # Aggregate cross-account insights
    total_accounts = len(accounts)
    total_findings = sum(len(result.get('findings', [])) for result in security_results)
    total_cost = sum(result.get('total_security_cost', 0) for result in cost_results)
    
    # Calculate organization-wide security score
    scores = [result.get('security_score', 0) for result in security_results if 'security_score' in result]
    avg_security_score = sum(scores) / len(scores) if scores else 0
    
    return {
        'organization_summary': {
            'total_accounts_analyzed': total_accounts,
            'average_security_score': round(avg_security_score, 1),
            'total_security_findings': total_findings,
            'total_monthly_security_cost': round(total_cost, 2)
        },
        'account_details': [
            {
                'account': accounts[i],
                'security_analysis': security_results[i],
                'cost_analysis': cost_results[i]
            }
            for i in range(len(accounts))
        ]
    }

if __name__ == "__main__":
    result = asyncio.run(analyze_all_accounts())
    print(json.dumps(result, indent=2))
