#!/usr/bin/env python3
"""Enable AWS Security Services for Real Data"""

import boto3

def enable_guardduty(region='us-east-1'):
    """Enable GuardDuty"""
    try:
        guardduty = boto3.client('guardduty', region_name=region)
        response = guardduty.create_detector(Enable=True)
        print(f"✅ GuardDuty enabled: {response['DetectorId']}")
        return True
    except Exception as e:
        print(f"❌ GuardDuty failed: {e}")
        return False

def enable_security_hub(region='us-east-1'):
    """Enable Security Hub"""
    try:
        securityhub = boto3.client('securityhub', region_name=region)
        securityhub.enable_security_hub()
        print("✅ Security Hub enabled")
        return True
    except Exception as e:
        print(f"❌ Security Hub failed: {e}")
        return False

def enable_cloudtrail(region='us-east-1'):
    """Enable CloudTrail"""
    try:
        cloudtrail = boto3.client('cloudtrail', region_name=region)
        s3 = boto3.client('s3', region_name=region)
        
        # Create S3 bucket for CloudTrail
        bucket_name = f"cloudtrail-logs-{boto3.Session().region_name}-{hash(boto3.Session().get_credentials().access_key) % 10000}"
        s3.create_bucket(Bucket=bucket_name)
        
        # Create CloudTrail
        cloudtrail.create_trail(
            Name='security-analysis-trail',
            S3BucketName=bucket_name,
            IncludeGlobalServiceEvents=True,
            IsMultiRegionTrail=True
        )
        
        cloudtrail.start_logging(Name='security-analysis-trail')
        print(f"✅ CloudTrail enabled: security-analysis-trail")
        return True
    except Exception as e:
        print(f"❌ CloudTrail failed: {e}")
        return False

def setup_config_rules():
    """Add some Config rules for compliance checking"""
    try:
        config = boto3.client('config', region_name='us-east-1')
        
        # Add a basic rule
        config.put_config_rule(
            ConfigRule={
                'ConfigRuleName': 'root-mfa-enabled',
                'Source': {
                    'Owner': 'AWS',
                    'SourceIdentifier': 'ROOT_MFA_ENABLED'
                }
            }
        )
        print("✅ Config rule added: root-mfa-enabled")
        return True
    except Exception as e:
        print(f"❌ Config rule failed: {e}")
        return False

if __name__ == "__main__":
    print("🔧 Enabling AWS Security Services...")
    
    enable_guardduty()
    enable_security_hub() 
    enable_cloudtrail()
    setup_config_rules()
    
    print("\n⏳ Services are starting up (takes 5-10 minutes)")
    print("   Run security analysis again in 10 minutes for real data!")
