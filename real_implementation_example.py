#!/usr/bin/env python3
"""
Example: What REAL implementation would look like
(This would replace the mock data in our Lambda function)
"""

import boto3
from datetime import datetime, timedelta

def get_real_security_costs(account_id):
    """Get ACTUAL security costs from AWS Cost Explorer"""
    
    cost_client = boto3.client('ce', region_name='us-east-1')
    
    # Get last 30 days
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
    
    try:
        response = cost_client.get_cost_and_usage(
            TimePeriod={
                'Start': start_date,
                'End': end_date
            },
            Granularity='MONTHLY',
            Metrics=['BlendedCost'],
            GroupBy=[
                {
                    'Type': 'DIMENSION',
                    'Key': 'SERVICE'
                }
            ],
            Filter={
                'Dimensions': {
                    'Key': 'SERVICE',
                    'Values': [
                        'Amazon GuardDuty',
                        'AWS Security Hub', 
                        'Amazon Inspector',
                        'AWS Config',
                        'AWS CloudTrail'
                    ]
                }
            }
        )
        
        # Parse actual costs
        actual_costs = {}
        total_cost = 0
        
        for result in response['ResultsByTime']:
            for group in result['Groups']:
                service = group['Keys'][0]
                cost = float(group['Metrics']['BlendedCost']['Amount'])
                actual_costs[service] = cost
                total_cost += cost
        
        return {
            'total_security_cost': round(total_cost, 2),
            'service_costs': actual_costs,
            'period_days': 30,
            'currency': 'USD'
        }
        
    except Exception as e:
        return {'error': f'Could not retrieve costs: {str(e)}'}

def get_real_security_findings(account_id):
    """Get ACTUAL security findings from Security Hub"""
    
    securityhub_client = boto3.client('securityhub', region_name='us-east-1')
    
    try:
        response = securityhub_client.get_findings(
            Filters={
                'RecordState': [{'Value': 'ACTIVE', 'Comparison': 'EQUALS'}]
            },
            MaxResults=100
        )
        
        # Count findings by severity
        findings_count = {'CRITICAL': 0, 'HIGH': 0, 'MEDIUM': 0, 'LOW': 0}
        
        for finding in response['Findings']:
            severity = finding['Severity']['Label']
            findings_count[severity] = findings_count.get(severity, 0) + 1
        
        return {
            'critical_findings': findings_count['CRITICAL'],
            'high_findings': findings_count['HIGH'], 
            'medium_findings': findings_count['MEDIUM'],
            'low_findings': findings_count['LOW'],
            'total_findings': sum(findings_count.values())
        }
        
    except Exception as e:
        return {'error': f'Security Hub not enabled or accessible: {str(e)}'}

# Test what YOUR account actually has
print("🔍 CHECKING YOUR ACTUAL AWS ACCOUNT")
print("="*40)

try:
    real_costs = get_real_security_costs('039920874011')
    if 'error' in real_costs:
        print(f"💰 Costs: {real_costs['error']}")
        print("   → This is why we use mock data for demo")
    else:
        print(f"💰 Real Costs: ${real_costs['total_security_cost']}")
        
except Exception as e:
    print(f"💰 Cost API Error: {e}")
    print("   → Your account likely has no security service costs")

try:
    real_findings = get_real_security_findings('039920874011')
    if 'error' in real_findings:
        print(f"🔍 Findings: {real_findings['error']}")
        print("   → Security Hub not enabled = no findings")
    else:
        print(f"🔍 Real Findings: {real_findings['total_findings']} total")
        
except Exception as e:
    print(f"🔍 Security Hub Error: {e}")
    print("   → Security Hub not enabled in your account")

print(f"\n💡 EXPLANATION:")
print("   • Your account has no security services enabled")
print("   • No costs because services aren't running")
print("   • Demo uses mock data to show what enterprise accounts see")
print("   • Real implementation would check if services exist first")
