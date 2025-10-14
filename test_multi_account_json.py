#!/usr/bin/env python3
import asyncio
import json
import sys
from account_discovery import get_organization_accounts, get_target_accounts
from multi_account_orchestrator import analyze_all_accounts

def run_analysis(config):
    """Run analysis based on JSON configuration"""
    mode = config.get('mode', 'single')
    
    if mode == 'single':
        from well_architected_security_agentcore import analyze_security_posture
        from cost_analysis_agentcore import get_security_costs
        
        account_id = config.get('account_id')
        if not account_id:
            accounts = get_target_accounts()
            account_id = accounts[0] if accounts else "unknown"
        
        security = analyze_security_posture(account_id)
        costs = get_security_costs(account_id)
        
        return {
            'mode': 'single_account',
            'account_id': account_id,
            'security_analysis': security,
            'cost_analysis': costs
        }
    
    elif mode == 'multiple':
        from well_architected_security_agentcore import analyze_security_posture
        from cost_analysis_agentcore import get_security_costs
        
        account_list = config.get('accounts', [])
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
    
    elif mode == 'org':
        result = asyncio.run(analyze_all_accounts())
        result['mode'] = 'entire_organization'
        return result

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 test_multi_account_json.py config.json")
        print("\nExample configs:")
        print('{"mode": "single"}')
        print('{"mode": "single", "account_id": "123456789012"}')
        print('{"mode": "multiple", "accounts": ["123456789012", "987654321098"]}')
        print('{"mode": "org"}')
        return
    
    config_file = sys.argv[1]
    
    try:
        with open(config_file, 'r') as f:
            config = json.load(f)
    except FileNotFoundError:
        # Try parsing as JSON string
        try:
            config = json.loads(config_file)
        except:
            print(f"Error: Cannot read config file or parse JSON: {config_file}")
            return
    
    result = run_analysis(config)
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
