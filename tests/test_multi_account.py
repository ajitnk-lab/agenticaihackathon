#!/usr/bin/env python3
import asyncio
import json
import sys
from src.utils.account_discovery import get_organization_accounts, get_target_accounts
from src.utils.multi_account_orchestrator import analyze_all_accounts

def test_single_account(account_id=None):
    """Test single account analysis"""
    from well_architected_security_agentcore import analyze_security_posture
    from cost_analysis_agentcore import get_security_costs
    
    if not account_id:
        accounts = get_target_accounts()
        account_id = accounts[0] if accounts else "unknown"
    
    print(f"🔍 Analyzing single account: {account_id}")
    
    security = analyze_security_posture(account_id)
    costs = get_security_costs(account_id)
    
    return {
        'mode': 'single_account',
        'account_id': account_id,
        'security_analysis': security,
        'cost_analysis': costs
    }

def test_multiple_accounts(account_list):
    """Test specific list of accounts"""
    from well_architected_security_agentcore import analyze_security_posture
    from cost_analysis_agentcore import get_security_costs
    
    print(f"🔍 Analyzing {len(account_list)} specific accounts")
    
    results = []
    for account_id in account_list:
        security = analyze_security_posture(account_id)
        costs = get_security_costs(account_id)
        results.append({
            'account_id': account_id,
            'security_analysis': security,
            'cost_analysis': costs
        })
    
    return {
        'mode': 'multiple_accounts',
        'total_accounts': len(account_list),
        'results': results
    }

async def test_entire_org():
    """Test entire organization analysis"""
    print("🏢 Analyzing entire organization")
    
    result = await analyze_all_accounts()
    result['mode'] = 'entire_organization'
    return result

def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python test_multi_account.py single [account_id]")
        print("  python test_multi_account.py multiple account1,account2,account3")
        print("  python test_multi_account.py org")
        return
    
    mode = sys.argv[1].lower()
    
    if mode == 'single':
        account_id = sys.argv[2] if len(sys.argv) > 2 else None
        result = test_single_account(account_id)
        
    elif mode == 'multiple':
        if len(sys.argv) < 3:
            print("Error: Provide comma-separated account IDs")
            return
        account_list = sys.argv[2].split(',')
        result = test_multiple_accounts(account_list)
        
    elif mode == 'org':
        result = asyncio.run(test_entire_org())
        
    else:
        print("Error: Mode must be 'single', 'multiple', or 'org'")
        return
    
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
