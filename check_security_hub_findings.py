#!/usr/bin/env python3
"""
Check Security Hub findings in detail
"""

import boto3
import json
from datetime import datetime

def get_security_hub_findings():
    """Get detailed Security Hub findings"""
    print("🛡️ SECURITY HUB FINDINGS ANALYSIS:")
    
    try:
        securityhub = boto3.client('securityhub')
        
        # Get findings with different filters
        filters = [
            ("All findings", {}),
            ("Critical/High", {
                'SeverityLabel': [
                    {'Value': 'CRITICAL', 'Comparison': 'EQUALS'},
                    {'Value': 'HIGH', 'Comparison': 'EQUALS'}
                ]
            }),
            ("Active findings", {
                'RecordState': [{'Value': 'ACTIVE', 'Comparison': 'EQUALS'}]
            })
        ]
        
        for desc, filter_criteria in filters:
            try:
                response = securityhub.get_findings(
                    Filters=filter_criteria,
                    MaxResults=50
                )
                
                findings = response.get('Findings', [])
                print(f"\n   📋 {desc}: {len(findings)} findings")
                
                # Analyze findings
                severity_counts = {}
                compliance_status = {}
                
                for finding in findings:
                    # Severity analysis
                    severity = finding.get('Severity', {}).get('Label', 'UNKNOWN')
                    severity_counts[severity] = severity_counts.get(severity, 0) + 1
                    
                    # Compliance status
                    compliance = finding.get('Compliance', {}).get('Status', 'UNKNOWN')
                    compliance_status[compliance] = compliance_status.get(compliance, 0) + 1
                    
                    # Show sample finding details
                    if len(findings) <= 5:  # Show details for small sets
                        print(f"      🔍 Finding: {finding.get('Title', 'No title')}")
                        print(f"         Severity: {severity}")
                        print(f"         Status: {finding.get('RecordState', 'Unknown')}")
                        print(f"         Compliance: {compliance}")
                        print(f"         Resource: {finding.get('Resources', [{}])[0].get('Id', 'Unknown')}")
                        print(f"         Description: {finding.get('Description', 'No description')[:100]}...")
                
                if severity_counts:
                    print(f"      Severity breakdown: {severity_counts}")
                if compliance_status:
                    print(f"      Compliance status: {compliance_status}")
                    
            except Exception as e:
                print(f"   ❌ {desc} error: {e}")
        
        # Get insight results
        try:
            insights = securityhub.get_insights(MaxResults=10)
            print(f"\n   💡 Security Insights: {len(insights.get('Insights', []))}")
            
            for insight in insights.get('Insights', []):
                print(f"      {insight.get('Name', 'Unnamed insight')}")
                
        except Exception as e:
            print(f"   ❌ Insights error: {e}")
            
    except Exception as e:
        print(f"   ❌ Security Hub error: {e}")

def check_config_evaluations():
    """Check Config rule evaluations in detail"""
    print("\n⚙️ CONFIG RULE EVALUATIONS:")
    
    try:
        config = boto3.client('config')
        
        # Get compliance summary
        try:
            summary = config.get_compliance_summary_by_config_rule()
            compliance_summary = summary.get('ComplianceSummary', {})
            print(f"   Overall Compliance Summary: {compliance_summary}")
            
        except Exception as e:
            print(f"   ❌ Compliance summary error: {e}")
        
        # Check individual rules
        rules = config.describe_config_rules()
        print(f"\n   📋 Checking {len(rules.get('ConfigRules', []))} Config rules:")
        
        total_evaluations = 0
        compliance_counts = {'COMPLIANT': 0, 'NON_COMPLIANT': 0, 'NOT_APPLICABLE': 0}
        
        for rule in rules.get('ConfigRules', [])[:10]:  # Check first 10 rules
            rule_name = rule['ConfigRuleName']
            
            try:
                # Get compliance by rule
                compliance = config.get_compliance_details_by_config_rule(
                    ConfigRuleName=rule_name,
                    Limit=50
                )
                
                evaluations = compliance.get('EvaluationResults', [])
                total_evaluations += len(evaluations)
                
                rule_compliance = {}
                for evaluation in evaluations:
                    status = evaluation.get('ComplianceType', 'UNKNOWN')
                    rule_compliance[status] = rule_compliance.get(status, 0) + 1
                    compliance_counts[status] = compliance_counts.get(status, 0) + 1
                
                if evaluations:
                    print(f"      ✅ {rule_name}: {len(evaluations)} evaluations - {rule_compliance}")
                else:
                    print(f"      ⚠️ {rule_name}: No evaluations found")
                    
            except Exception as e:
                print(f"      ❌ {rule_name}: Error - {e}")
        
        print(f"\n   📊 Total evaluations: {total_evaluations}")
        print(f"   📊 Compliance breakdown: {compliance_counts}")
        
    except Exception as e:
        print(f"   ❌ Config error: {e}")

if __name__ == "__main__":
    print("🔍 DETAILED SECURITY FINDINGS ANALYSIS")
    print(f"⏰ Analysis Started: {datetime.now().isoformat()}")
    
    get_security_hub_findings()
    check_config_evaluations()
    
    print(f"\n⏰ Analysis Completed: {datetime.now().isoformat()}")
