#!/usr/bin/env python3
import json
import sys
import os
from datetime import datetime
import boto3

def lambda_handler(event, context):
    """Handle requests using REAL AWS data directly"""
    
    try:
        # Get real security data directly
        security_data = get_real_security_data()
        cost_data = get_real_cost_data()
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'security_data': security_data,
                'cost_data': cost_data,
                'timestamp': datetime.now().isoformat(),
                'data_source': 'real_aws_apis'
            })
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'error': str(e),
                'data_source': 'error'
            })
        }

def get_real_security_data():
    """Get real security data from AWS APIs"""
    try:
        # Try Security Hub first
        securityhub = boto3.client('securityhub', region_name='us-east-1')
        
        response = securityhub.get_findings(
            Filters={
                'RecordState': [{'Value': 'ACTIVE', 'Comparison': 'EQUALS'}]
            },
            MaxResults=50
        )
        
        findings = response.get('Findings', [])
        total_findings = len(findings)
        
        # Calculate security score based on findings
        critical_count = sum(1 for f in findings if f.get('Severity', {}).get('Label') == 'CRITICAL')
        high_count = sum(1 for f in findings if f.get('Severity', {}).get('Label') == 'HIGH')
        
        # Simple scoring: start at 100, deduct points for findings
        security_score = max(0, 100 - (critical_count * 10) - (high_count * 5) - (total_findings * 1))
        
        return {
            'security_score': int(security_score),
            'total_findings': total_findings,
            'critical_findings': critical_count,
            'high_findings': high_count,
            'data_source': 'security_hub'
        }
        
    except Exception as e:
        # Fallback to Config if Security Hub fails
        try:
            return get_config_compliance_data()
        except Exception as e2:
            # Final fallback with error info
            return {
                'security_score': 0,
                'total_findings': 0,
                'error': f'Security Hub: {str(e)}, Config: {str(e2)}',
                'data_source': 'error_fallback'
            }

def get_config_compliance_data():
    """Get compliance data from AWS Config"""
    config = boto3.client('config', region_name='us-east-1')
    
    # Get compliance summary
    response = config.get_compliance_summary_by_config_rule()
    
    compliant = response.get('ComplianceSummary', {}).get('CompliantResourceCount', {}).get('CappedCount', 0)
    non_compliant = response.get('ComplianceSummary', {}).get('NonCompliantResourceCount', {}).get('CappedCount', 0)
    
    total_rules = compliant + non_compliant
    compliance_rate = (compliant / max(total_rules, 1)) * 100 if total_rules > 0 else 0
    
    return {
        'security_score': int(compliance_rate),
        'total_findings': non_compliant,
        'compliant_rules': compliant,
        'non_compliant_rules': non_compliant,
        'data_source': 'aws_config'
    }

def get_real_cost_data():
    """Get real cost data from Cost Explorer"""
    try:
        ce = boto3.client('ce', region_name='us-east-1')
        
        # Get last month's costs for security services
        from datetime import datetime, timedelta
        end_date = datetime.now().replace(day=1)
        start_date = (end_date - timedelta(days=32)).replace(day=1)
        
        response = ce.get_cost_and_usage(
            TimePeriod={
                'Start': start_date.strftime('%Y-%m-%d'),
                'End': end_date.strftime('%Y-%m-%d')
            },
            Granularity='MONTHLY',
            Metrics=['UnblendedCost'],
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
                    ],
                    'MatchOptions': ['EQUALS']
                }
            }
        )
        
        total_cost = 0
        service_costs = {}
        
        for result in response.get('ResultsByTime', []):
            for group in result.get('Groups', []):
                service_name = group['Keys'][0]
                cost = float(group['Metrics']['UnblendedCost']['Amount'])
                total_cost += cost
                service_costs[service_name] = cost
        
        return {
            'total_monthly_cost': round(total_cost, 2),
            'service_costs': service_costs,
            'data_source': 'cost_explorer'
        }
        
    except Exception as e:
        return {
            'total_monthly_cost': 0,
            'error': str(e),
            'data_source': 'cost_error'
        }
