#!/usr/bin/env python3
"""
Diagnose AWS Services - Check what's actually enabled and has data
"""

import boto3
import json
from datetime import datetime, timedelta

def check_inspector_status():
    """Check if Inspector is enabled and has findings"""
    print("🔍 INSPECTOR V2 STATUS:")
    
    try:
        inspector = boto3.client('inspector2')
        
        # Check if Inspector is enabled
        try:
            status = inspector.batch_get_account_status(accountIds=[boto3.client('sts').get_caller_identity()['Account']])
            print(f"   Account Status: {status}")
        except Exception as e:
            print(f"   ❌ Account status error: {e}")
        
        # List findings with different filters
        print("\n   📋 Checking findings with different time ranges:")
        
        time_ranges = [
            ("Last 7 days", 7),
            ("Last 30 days", 30), 
            ("Last 90 days", 90),
            ("Last 365 days", 365)
        ]
        
        for desc, days in time_ranges:
            try:
                response = inspector.list_findings(
                    filterCriteria={
                        'updatedAt': [{
                            'startInclusive': datetime.now() - timedelta(days=days),
                            'endInclusive': datetime.now()
                        }]
                    },
                    maxResults=10
                )
                findings_count = len(response.get('findings', []))
                print(f"   {desc}: {findings_count} findings")
                
                if findings_count > 0:
                    print(f"      Sample finding: {response['findings'][0].get('title', 'No title')}")
                    
            except Exception as e:
                print(f"   {desc}: Error - {e}")
        
        # Check without time filter
        try:
            response = inspector.list_findings(maxResults=10)
            total_findings = len(response.get('findings', []))
            print(f"   All findings (no time filter): {total_findings}")
        except Exception as e:
            print(f"   All findings error: {e}")
            
    except Exception as e:
        print(f"   ❌ Inspector client error: {e}")

def check_config_status():
    """Check Config service status and rules"""
    print("\n⚙️ AWS CONFIG STATUS:")
    
    try:
        config = boto3.client('config')
        
        # Check Config recorder status
        try:
            recorders = config.describe_configuration_recorders()
            print(f"   Configuration Recorders: {len(recorders.get('ConfigurationRecorders', []))}")
            
            for recorder in recorders.get('ConfigurationRecorders', []):
                print(f"      Name: {recorder.get('name')}")
                print(f"      Recording: {recorder.get('recordingGroup', {})}")
        except Exception as e:
            print(f"   ❌ Recorder error: {e}")
        
        # Check delivery channels
        try:
            channels = config.describe_delivery_channels()
            print(f"   Delivery Channels: {len(channels.get('DeliveryChannels', []))}")
        except Exception as e:
            print(f"   ❌ Delivery channels error: {e}")
        
        # Check Config rules
        try:
            rules = config.describe_config_rules()
            print(f"   Config Rules: {len(rules.get('ConfigRules', []))}")
            
            # Check compliance for each rule
            compliance_summary = {'COMPLIANT': 0, 'NON_COMPLIANT': 0, 'NOT_APPLICABLE': 0}
            
            for rule in rules.get('ConfigRules', [])[:5]:  # Check first 5 rules
                rule_name = rule['ConfigRuleName']
                try:
                    compliance = config.get_compliance_details_by_config_rule(
                        ConfigRuleName=rule_name,
                        Limit=10
                    )
                    
                    results = compliance.get('EvaluationResults', [])
                    print(f"      Rule '{rule_name}': {len(results)} evaluations")
                    
                    for result in results:
                        status = result.get('ComplianceType', 'UNKNOWN')
                        compliance_summary[status] = compliance_summary.get(status, 0) + 1
                        
                except Exception as e:
                    print(f"      Rule '{rule_name}': Error - {e}")
            
            print(f"   Compliance Summary: {compliance_summary}")
            
        except Exception as e:
            print(f"   ❌ Config rules error: {e}")
            
    except Exception as e:
        print(f"   ❌ Config client error: {e}")

def check_cost_explorer_data():
    """Check Cost Explorer for actual spending data"""
    print("\n💰 COST EXPLORER DATA:")
    
    try:
        ce = boto3.client('ce')
        
        # Check different time periods
        time_periods = [
            ("Last 7 days", 7),
            ("Last 30 days", 30),
            ("Last 90 days", 90)
        ]
        
        for desc, days in time_periods:
            end_date = datetime.now().date()
            start_date = end_date - timedelta(days=days)
            
            try:
                # Get total costs
                response = ce.get_cost_and_usage(
                    TimePeriod={
                        'Start': start_date.strftime('%Y-%m-%d'),
                        'End': end_date.strftime('%Y-%m-%d')
                    },
                    Granularity='MONTHLY',
                    Metrics=['UnblendedCost']
                )
                
                total_cost = 0
                for result in response.get('ResultsByTime', []):
                    for group in result.get('Groups', []):
                        amount = float(group.get('Metrics', {}).get('UnblendedCost', {}).get('Amount', 0))
                        total_cost += amount
                
                print(f"   {desc}: ${total_cost:.2f}")
                
                # Check specific security services
                security_services = ['GuardDuty', 'Security Hub', 'Inspector', 'Config']
                
                for service in security_services:
                    try:
                        service_response = ce.get_cost_and_usage(
                            TimePeriod={
                                'Start': start_date.strftime('%Y-%m-%d'),
                                'End': end_date.strftime('%Y-%m-%d')
                            },
                            Granularity='MONTHLY',
                            Metrics=['UnblendedCost'],
                            GroupBy=[{'Type': 'DIMENSION', 'Key': 'SERVICE'}],
                            Filter={
                                'Dimensions': {
                                    'Key': 'SERVICE',
                                    'Values': [f'Amazon {service}', f'AWS {service}'],
                                    'MatchOptions': ['CONTAINS']
                                }
                            }
                        )
                        
                        service_cost = 0
                        for result in service_response.get('ResultsByTime', []):
                            for group in result.get('Groups', []):
                                amount = float(group.get('Metrics', {}).get('UnblendedCost', {}).get('Amount', 0))
                                service_cost += amount
                        
                        print(f"      {service}: ${service_cost:.2f}")
                        
                    except Exception as e:
                        print(f"      {service}: Error - {e}")
                        
            except Exception as e:
                print(f"   {desc}: Error - {e}")
                
    except Exception as e:
        print(f"   ❌ Cost Explorer error: {e}")

def check_security_services_enabled():
    """Check if security services are actually enabled"""
    print("\n🛡️ SECURITY SERVICES STATUS:")
    
    # GuardDuty
    try:
        guardduty = boto3.client('guardduty')
        detectors = guardduty.list_detectors()
        print(f"   GuardDuty Detectors: {len(detectors.get('DetectorIds', []))}")
        
        for detector_id in detectors.get('DetectorIds', []):
            detector = guardduty.get_detector(DetectorId=detector_id)
            print(f"      Detector {detector_id}: Status = {detector.get('Status')}")
            
    except Exception as e:
        print(f"   ❌ GuardDuty error: {e}")
    
    # Security Hub
    try:
        securityhub = boto3.client('securityhub')
        hub = securityhub.describe_hub()
        print(f"   Security Hub: {hub.get('HubArn', 'Not found')}")
        
        # Get findings
        findings = securityhub.get_findings(MaxResults=10)
        print(f"   Security Hub Findings: {len(findings.get('Findings', []))}")
        
    except Exception as e:
        print(f"   ❌ Security Hub error: {e}")

def check_cloudwatch_data():
    """Check CloudWatch for metrics and logs"""
    print("\n📊 CLOUDWATCH DATA:")
    
    try:
        cloudwatch = boto3.client('cloudwatch')
        
        # List some common security-related metrics
        metrics_to_check = [
            ('AWS/GuardDuty', 'FindingCount'),
            ('AWS/Inspector', 'TotalFindings'),
            ('AWS/Config', 'ComplianceByConfigRule')
        ]
        
        for namespace, metric_name in metrics_to_check:
            try:
                metrics = cloudwatch.list_metrics(
                    Namespace=namespace,
                    MetricName=metric_name
                )
                print(f"   {namespace}/{metric_name}: {len(metrics.get('Metrics', []))} metrics")
                
            except Exception as e:
                print(f"   {namespace}/{metric_name}: Error - {e}")
                
    except Exception as e:
        print(f"   ❌ CloudWatch error: {e}")

if __name__ == "__main__":
    print("🔍 AWS SERVICES DIAGNOSTIC - Why are we seeing 0/100 values?")
    print(f"⏰ Diagnostic Started: {datetime.now().isoformat()}")
    
    # Get current account info
    try:
        sts = boto3.client('sts')
        identity = sts.get_caller_identity()
        print(f"🆔 Account: {identity.get('Account')} | Region: {boto3.Session().region_name}")
    except Exception as e:
        print(f"❌ Identity error: {e}")
    
    check_inspector_status()
    check_config_status()
    check_security_services_enabled()
    check_cost_explorer_data()
    check_cloudwatch_data()
    
    print(f"\n⏰ Diagnostic Completed: {datetime.now().isoformat()}")
    print("\n💡 ANALYSIS:")
    print("   - If all services show 0 findings/costs, they may not be enabled")
    print("   - If services are enabled but no data, check time ranges")
    print("   - Cost data may take 24-48 hours to appear in Cost Explorer")
    print("   - Some services require explicit enablement in each region")
