#!/usr/bin/env python3
"""
Get Real Security Data from Security Hub (which has actual findings)
"""

import boto3
import json
from datetime import datetime, timedelta

def get_security_hub_findings(region: str = "us-east-1"):
    """Get real findings from Security Hub"""
    try:
        securityhub = boto3.client('securityhub', region_name=region)
        
        # Get all active findings
        response = securityhub.get_findings(
            Filters={
                'RecordState': [{'Value': 'ACTIVE', 'Comparison': 'EQUALS'}]
            },
            MaxResults=100
        )
        
        findings = response.get('Findings', [])
        
        # Categorize by severity
        severity_counts = {'CRITICAL': 0, 'HIGH': 0, 'MEDIUM': 0, 'LOW': 0, 'INFORMATIONAL': 0}
        compliance_counts = {'FAILED': 0, 'WARNING': 0, 'PASSED': 0, 'NOT_AVAILABLE': 0}
        
        sample_findings = []
        
        for finding in findings:
            severity = finding.get('Severity', {}).get('Label', 'UNKNOWN')
            compliance = finding.get('Compliance', {}).get('Status', 'UNKNOWN')
            
            if severity in severity_counts:
                severity_counts[severity] += 1
            
            if compliance in compliance_counts:
                compliance_counts[compliance] += 1
            
            # Collect sample findings
            if len(sample_findings) < 5:
                sample_findings.append({
                    'title': finding.get('Title', 'No title'),
                    'severity': severity,
                    'compliance': compliance,
                    'resource': finding.get('Resources', [{}])[0].get('Id', 'Unknown'),
                    'description': finding.get('Description', 'No description')[:200]
                })
        
        return {
            'service': 'Security Hub',
            'total_findings': len(findings),
            'severity_breakdown': severity_counts,
            'compliance_breakdown': compliance_counts,
            'sample_findings': sample_findings,
            'status': 'success'
        }
        
    except Exception as e:
        return {'service': 'Security Hub', 'error': str(e), 'status': 'error'}

def get_inspector_findings(region: str = "us-east-1"):
    """Get real findings from Inspector (keeping for compatibility)"""
    try:
        inspector = boto3.client('inspector2', region_name=region)
        
        # Check if Inspector is enabled first
        sts = boto3.client('sts')
        account_id = sts.get_caller_identity()['Account']
        
        status_response = inspector.batch_get_account_status(accountIds=[account_id])
        account_status = status_response.get('accounts', [{}])[0].get('state', {}).get('status', 'UNKNOWN')
        
        if account_status == 'DISABLED':
            return {
                'service': 'Inspector',
                'total_findings': 0,
                'severity_breakdown': {'CRITICAL': 0, 'HIGH': 0, 'MEDIUM': 0, 'LOW': 0},
                'sample_findings': [],
                'status': 'disabled',
                'message': 'Inspector is disabled in this account'
            }
        
        # Get findings from last 30 days
        response = inspector.list_findings(
            filterCriteria={
                'updatedAt': [{
                    'startInclusive': datetime.now() - timedelta(days=30),
                    'endInclusive': datetime.now()
                }]
            },
            maxResults=50
        )
        
        findings = response.get('findings', [])
        
        # Categorize by severity
        severity_counts = {'CRITICAL': 0, 'HIGH': 0, 'MEDIUM': 0, 'LOW': 0}
        
        for finding in findings:
            severity = finding.get('severity', 'UNKNOWN')
            if severity in severity_counts:
                severity_counts[severity] += 1
        
        return {
            'service': 'Inspector',
            'total_findings': len(findings),
            'severity_breakdown': severity_counts,
            'sample_findings': findings[:3],
            'status': 'success'
        }
        
    except Exception as e:
        return {'service': 'Inspector', 'error': str(e), 'status': 'error'}

def get_config_compliance(region: str = "us-east-1"):
    """Get real compliance data from Config"""
    try:
        config = boto3.client('config', region_name=region)
        
        # Get overall compliance summary
        try:
            summary = config.get_compliance_summary_by_config_rule()
            compliance_summary = summary.get('ComplianceSummary', {})
            
            compliant = compliance_summary.get('CompliantResourceCount', {}).get('CappedCount', 0)
            non_compliant = compliance_summary.get('NonCompliantResourceCount', {}).get('CappedCount', 0)
            total_resources = compliant + non_compliant
            
        except Exception:
            # Fallback: count rules directly
            rules_response = config.describe_config_rules()
            total_rules = len(rules_response.get('ConfigRules', []))
            compliant = 0
            non_compliant = 0
            
            # Check a few rules for actual evaluations
            for rule in rules_response.get('ConfigRules', [])[:5]:
                try:
                    rule_compliance = config.get_compliance_details_by_config_rule(
                        ConfigRuleName=rule['ConfigRuleName'],
                        Limit=10
                    )
                    evaluations = rule_compliance.get('EvaluationResults', [])
                    
                    for evaluation in evaluations:
                        if evaluation.get('ComplianceType') == 'COMPLIANT':
                            compliant += 1
                        else:
                            non_compliant += 1
                            
                except Exception:
                    continue
            
            total_resources = compliant + non_compliant
        
        # Get specific rule details
        rules_response = config.describe_config_rules()
        rules = rules_response.get('ConfigRules', [])
        
        return {
            'service': 'Config',
            'total_rules': len(rules),
            'compliant_resources': compliant,
            'non_compliant_resources': non_compliant,
            'total_resources': total_resources,
            'compliance_rate': (compliant / total_resources * 100) if total_resources > 0 else 100,
            'active_rules': len(rules),
            'status': 'success'
        }
        
    except Exception as e:
        return {'service': 'Config', 'error': str(e), 'status': 'error'}

def get_real_security_assessment(account_id: str, region: str = "us-east-1"):
    """Get real security assessment using Security Hub + Config"""
    
    print(f"🔍 Getting real security data for account {account_id}...")
    
    # Get data from Security Hub (primary source) and Config
    security_hub_data = get_security_hub_findings(region)
    config_data = get_config_compliance(region)
    
    # Calculate overall security score based on real Security Hub findings
    security_score = 100
    
    # Deduct points for Security Hub findings
    if security_hub_data['status'] == 'success':
        critical = security_hub_data['severity_breakdown']['CRITICAL']
        high = security_hub_data['severity_breakdown']['HIGH']
        medium = security_hub_data['severity_breakdown']['MEDIUM']
        low = security_hub_data['severity_breakdown']['LOW']
        
        # Scoring: -20 per critical, -10 per high, -5 per medium, -1 per low
        security_score -= (critical * 20 + high * 10 + medium * 5 + low * 1)
    
    # Factor in Config compliance
    if config_data['status'] == 'success':
        compliance_rate = config_data['compliance_rate']
        # If compliance is below 80%, deduct additional points
        if compliance_rate < 80:
            security_score -= (80 - compliance_rate) / 2
    
    # Ensure score doesn't go below 0
    security_score = max(0, security_score)
    
    return {
        'account_id': account_id,
        'region': region,
        'security_score': int(security_score),
        'security_hub_findings': security_hub_data,
        'config_compliance': config_data,
        'assessment_timestamp': datetime.now().isoformat(),
        'data_source': 'real_aws_services',
        'summary': {
            'total_findings': security_hub_data.get('total_findings', 0),
            'critical_findings': security_hub_data.get('severity_breakdown', {}).get('CRITICAL', 0),
            'high_findings': security_hub_data.get('severity_breakdown', {}).get('HIGH', 0),
            'compliance_rate': config_data.get('compliance_rate', 100)
        }
    }
