#!/usr/bin/env python3
"""Get Real Cost Data from AWS Cost Explorer"""

import boto3
from datetime import datetime, timedelta

def get_real_security_costs(account_id: str, days: int = 30):
    """Get actual security service costs from Cost Explorer"""
    try:
        ce = boto3.client('ce', region_name='us-east-1')
        
        # Date range for cost query
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days)
        
        # Security services to query
        security_services = [
            'Amazon GuardDuty',
            'AWS Security Hub', 
            'Amazon Inspector',
            'AWS Config',
            'AWS CloudTrail'
        ]
        
        total_cost = 0.0
        service_costs = {}
        
        for service in security_services:
            try:
                response = ce.get_cost_and_usage(
                    TimePeriod={
                        'Start': start_date.strftime('%Y-%m-%d'),
                        'End': end_date.strftime('%Y-%m-%d')
                    },
                    Granularity='MONTHLY',
                    Metrics=['UnblendedCost'],
                    GroupBy=[
                        {'Type': 'DIMENSION', 'Key': 'SERVICE'}
                    ],
                    Filter={
                        'Dimensions': {
                            'Key': 'SERVICE',
                            'Values': [service],
                            'MatchOptions': ['EQUALS']
                        }
                    }
                )
                
                # Extract cost from response
                cost = 0.0
                for result in response.get('ResultsByTime', []):
                    for group in result.get('Groups', []):
                        amount = float(group['Metrics']['UnblendedCost']['Amount'])
                        cost += amount
                
                service_costs[service] = round(cost, 2)
                total_cost += cost
                
            except Exception as e:
                print(f"Warning: Could not get cost for {service}: {e}")
                service_costs[service] = 0.0
        
        return {
            'account_id': account_id,
            'period_days': days,
            'total_security_cost': round(total_cost, 2),
            'service_costs': service_costs,
            'currency': 'USD',
            'data_source': 'aws_cost_explorer'
        }
        
    except Exception as e:
        print(f"Error getting real costs: {e}")
        # Fallback to estimated costs based on enabled services
        return get_estimated_costs(account_id, days)

def get_estimated_costs(account_id: str, days: int = 30):
    """Estimate costs based on enabled services"""
    try:
        # Check which services are actually enabled
        from src.utils.security_service_checker import check_security_services
        
        services_status = check_security_services(account_id)
        
        # Estimated monthly costs for enabled services
        estimated_costs = {
            'GuardDuty': 10.0 if services_status.get('GuardDuty') else 0.0,
            'SecurityHub': 5.0 if services_status.get('SecurityHub') else 0.0,
            'Inspector': 15.0 if services_status.get('Inspector') else 0.0,
            'Config': 8.0 if services_status.get('Config') else 0.0,
            'CloudTrail': 2.0 if services_status.get('CloudTrail') else 0.0
        }
        
        # Adjust for partial month
        multiplier = days / 30.0
        adjusted_costs = {k: round(v * multiplier, 2) for k, v in estimated_costs.items()}
        
        return {
            'account_id': account_id,
            'period_days': days,
            'total_security_cost': round(sum(adjusted_costs.values()), 2),
            'service_costs': adjusted_costs,
            'currency': 'USD',
            'data_source': 'estimated_based_on_enabled_services'
        }
        
    except Exception as e:
        return {
            'account_id': account_id,
            'error': str(e),
            'data_source': 'error'
        }

if __name__ == "__main__":
    # Test real cost retrieval
    import json
    costs = get_real_security_costs("039920874011")
    print(json.dumps(costs, indent=2))
