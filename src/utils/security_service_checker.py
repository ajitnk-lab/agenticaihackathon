#!/usr/bin/env python3
"""
Security Service Availability Checker
Checks if required AWS security services are enabled before analysis
"""

import boto3
from typing import Dict, List

def check_security_services(account_id: str, region: str = "us-east-1") -> Dict[str, bool]:
    """Check if required security services are enabled"""
    
    services_status = {
        "GuardDuty": False,
        "SecurityHub": False, 
        "Inspector": False,
        "Config": False,
        "CloudTrail": False
    }
    
    try:
        # Check GuardDuty
        guardduty = boto3.client('guardduty', region_name=region)
        detectors = guardduty.list_detectors()
        services_status["GuardDuty"] = len(detectors.get('DetectorIds', [])) > 0
        
        # Check Security Hub
        securityhub = boto3.client('securityhub', region_name=region)
        try:
            securityhub.describe_hub()
            services_status["SecurityHub"] = True
        except securityhub.exceptions.InvalidAccessException:
            services_status["SecurityHub"] = False
            
        # Check Inspector
        inspector = boto3.client('inspector2', region_name=region)
        try:
            inspector.batch_get_account_status(accountIds=[account_id])
            services_status["Inspector"] = True
        except Exception:
            services_status["Inspector"] = False
            
        # Check Config
        config = boto3.client('config', region_name=region)
        try:
            config.describe_configuration_recorders()
            services_status["Config"] = True
        except Exception:
            services_status["Config"] = False
            
        # Check CloudTrail
        cloudtrail = boto3.client('cloudtrail', region_name=region)
        trails = cloudtrail.describe_trails()
        services_status["CloudTrail"] = len(trails.get('trailList', [])) > 0
        
    except Exception as e:
        print(f"Error checking services: {e}")
    
    return services_status

def get_missing_services(services_status: Dict[str, bool]) -> List[str]:
    """Get list of missing/disabled services"""
    return [service for service, enabled in services_status.items() if not enabled]

def can_perform_analysis(services_status: Dict[str, bool]) -> bool:
    """Check if we have minimum services needed for analysis"""
    # Require at least GuardDuty OR Security Hub to be enabled
    return services_status.get("GuardDuty", False) or services_status.get("SecurityHub", False)

if __name__ == "__main__":
    # Test service availability
    status = check_security_services("039920874011")
    missing = get_missing_services(status)
    
    print("🔍 Security Services Status:")
    for service, enabled in status.items():
        print(f"   {service}: {'✅ Enabled' if enabled else '❌ Disabled'}")
    
    if missing:
        print(f"\n⚠️  Missing Services: {', '.join(missing)}")
    
    if can_perform_analysis(status):
        print("\n✅ Can perform security analysis")
    else:
        print("\n❌ Cannot perform analysis - enable GuardDuty or Security Hub first")
