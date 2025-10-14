import boto3
from typing import List, Dict

def get_organization_accounts(ou_id: str = None) -> List[Dict[str, str]]:
    """Get all AWS accounts in the organization or specific OU"""
    try:
        org_client = boto3.client('organizations')
        
        if ou_id:
            # Get accounts in specific OU
            response = org_client.list_accounts_for_parent(ParentId=ou_id)
        else:
            # Get all accounts in organization
            response = org_client.list_accounts()
        
        accounts = []
        for account in response['Accounts']:
            if account['Status'] == 'ACTIVE':
                accounts.append({
                    'id': account['Id'],
                    'name': account['Name'],
                    'email': account['Email']
                })
        
        return accounts
    except Exception as e:
        # Fallback to current account if Organizations not available
        sts_client = boto3.client('sts')
        current_account = sts_client.get_caller_identity()['Account']
        return [{'id': current_account, 'name': 'Current Account', 'email': ''}]

def get_target_accounts(account_filter: str = None, ou_id: str = None) -> List[str]:
    """Get list of account IDs to analyze"""
    accounts = get_organization_accounts(ou_id)
    
    if account_filter:
        # Filter by account name or ID
        accounts = [acc for acc in accounts if account_filter.lower() in acc['name'].lower() or account_filter in acc['id']]
    
    return [acc['id'] for acc in accounts]

def list_organizational_units() -> List[Dict[str, str]]:
    """List all OUs in the organization"""
    try:
        org_client = boto3.client('organizations')
        response = org_client.list_roots()
        root_id = response['Roots'][0]['Id']
        
        ous = []
        response = org_client.list_organizational_units_for_parent(ParentId=root_id)
        
        for ou in response['OrganizationalUnits']:
            ous.append({
                'id': ou['Id'],
                'name': ou['Name']
            })
        
        return ous
    except Exception:
        return []
