#!/usr/bin/env python3
"""
Enable AWS Security Services: Inspector, Access Analyzer, and Macie
"""

import boto3
import json
from datetime import datetime

def enable_inspector():
    """Enable Amazon Inspector v2"""
    print("🔍 Enabling Amazon Inspector v2...")
    
    try:
        inspector = boto3.client('inspector2')
        sts = boto3.client('sts')
        account_id = sts.get_caller_identity()['Account']
        
        # Enable Inspector for EC2 and ECR
        response = inspector.enable(
            accountIds=[account_id],
            resourceTypes=['EC2', 'ECR']
        )
        
        print(f"   ✅ Inspector enabled for account {account_id}")
        print(f"   📊 Resource types: EC2, ECR")
        return True
        
    except Exception as e:
        print(f"   ❌ Inspector enable failed: {e}")
        return False

def enable_access_analyzer():
    """Enable IAM Access Analyzer"""
    print("\n🔐 Enabling IAM Access Analyzer...")
    
    try:
        analyzer = boto3.client('accessanalyzer')
        
        # Create analyzer
        response = analyzer.create_analyzer(
            analyzerName='SecurityROIAnalyzer',
            type='ACCOUNT',
            tags={
                'Purpose': 'SecurityROICalculator',
                'CreatedBy': 'AgentCore'
            }
        )
        
        analyzer_arn = response['arn']
        print(f"   ✅ Access Analyzer created: {analyzer_arn}")
        return True
        
    except Exception as e:
        if "already exists" in str(e).lower():
            print("   ✅ Access Analyzer already exists")
            return True
        print(f"   ❌ Access Analyzer enable failed: {e}")
        return False

def enable_macie():
    """Enable Amazon Macie"""
    print("\n🛡️ Enabling Amazon Macie...")
    
    try:
        macie = boto3.client('macie2')
        
        # Enable Macie
        response = macie.enable_macie(
            findingPublishingFrequency='FIFTEEN_MINUTES',
            status='ENABLED'
        )
        
        print("   ✅ Macie enabled successfully")
        print("   📊 Finding frequency: Every 15 minutes")
        return True
        
    except Exception as e:
        if "already enabled" in str(e).lower():
            print("   ✅ Macie already enabled")
            return True
        print(f"   ❌ Macie enable failed: {e}")
        return False

def verify_services():
    """Verify all services are enabled"""
    print("\n✅ Verifying Security Services Status...")
    
    services_status = {}
    
    # Check GuardDuty
    try:
        guardduty = boto3.client('guardduty')
        detectors = guardduty.list_detectors()
        services_status['GuardDuty'] = len(detectors.get('DetectorIds', [])) > 0
    except:
        services_status['GuardDuty'] = False
    
    # Check Security Hub
    try:
        securityhub = boto3.client('securityhub')
        securityhub.describe_hub()
        services_status['SecurityHub'] = True
    except:
        services_status['SecurityHub'] = False
    
    # Check Inspector
    try:
        inspector = boto3.client('inspector2')
        sts = boto3.client('sts')
        account_id = sts.get_caller_identity()['Account']
        status = inspector.batch_get_account_status(accountIds=[account_id])
        services_status['Inspector'] = status['accounts'][0]['state']['status'] == 'ENABLED'
    except:
        services_status['Inspector'] = False
    
    # Check Access Analyzer
    try:
        analyzer = boto3.client('accessanalyzer')
        analyzers = analyzer.list_analyzers()
        services_status['AccessAnalyzer'] = len(analyzers.get('analyzers', [])) > 0
    except:
        services_status['AccessAnalyzer'] = False
    
    # Check Macie
    try:
        macie = boto3.client('macie2')
        session = macie.get_macie_session()
        services_status['Macie'] = session.get('status') == 'ENABLED'
    except:
        services_status['Macie'] = False
    
    # Print status
    print("\n📊 Final Security Services Status:")
    for service, enabled in services_status.items():
        status = "✅ ENABLED" if enabled else "❌ DISABLED"
        print(f"   {service}: {status}")
    
    enabled_count = sum(services_status.values())
    total_count = len(services_status)
    print(f"\n🎯 Summary: {enabled_count}/{total_count} services enabled")
    
    return services_status

def main():
    """Main function to enable security services"""
    print("🚀 ENABLING AWS SECURITY SERVICES")
    print(f"⏰ Started: {datetime.now().isoformat()}")
    
    results = {}
    
    # Enable services
    results['Inspector'] = enable_inspector()
    results['AccessAnalyzer'] = enable_access_analyzer()
    results['Macie'] = enable_macie()
    
    # Verify all services
    final_status = verify_services()
    
    # Summary
    print(f"\n{'='*60}")
    print("📋 ENABLEMENT SUMMARY")
    print('='*60)
    
    success_count = sum(results.values())
    total_attempts = len(results)
    
    for service, success in results.items():
        status = "✅ SUCCESS" if success else "❌ FAILED"
        print(f"   {service}: {status}")
    
    print(f"\n🎯 Enablement: {success_count}/{total_attempts} successful")
    
    if success_count == total_attempts:
        print("\n🎉 ALL SECURITY SERVICES ENABLED!")
        print("\n📋 Next Steps:")
        print("   • Wait 5-10 minutes for services to initialize")
        print("   • Run: python3 test_comprehensive_security.py")
        print("   • Check for new findings and data")
    else:
        print("\n⚠️ Some services failed to enable")
        print("   • Check AWS permissions")
        print("   • Verify account limits")
        print("   • Review error messages above")
    
    print(f"\n⏰ Completed: {datetime.now().isoformat()}")
    
    return success_count == total_attempts

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
