#!/usr/bin/env python3
"""Fix CloudTrail and Config Rule Issues"""

import boto3
import json

def fix_cloudtrail():
    """Fix CloudTrail with proper S3 bucket policy"""
    try:
        s3 = boto3.client('s3')
        cloudtrail = boto3.client('cloudtrail')
        account_id = boto3.client('sts').get_caller_identity()['Account']
        
        bucket_name = f"security-cloudtrail-{account_id}"
        
        # Create bucket
        s3.create_bucket(Bucket=bucket_name)
        
        # Set proper bucket policy for CloudTrail
        bucket_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Sid": "AWSCloudTrailAclCheck",
                    "Effect": "Allow",
                    "Principal": {"Service": "cloudtrail.amazonaws.com"},
                    "Action": "s3:GetBucketAcl",
                    "Resource": f"arn:aws:s3:::{bucket_name}"
                },
                {
                    "Sid": "AWSCloudTrailWrite",
                    "Effect": "Allow",
                    "Principal": {"Service": "cloudtrail.amazonaws.com"},
                    "Action": "s3:PutObject",
                    "Resource": f"arn:aws:s3:::{bucket_name}/*",
                    "Condition": {
                        "StringEquals": {
                            "s3:x-amz-acl": "bucket-owner-full-control"
                        }
                    }
                }
            ]
        }
        
        s3.put_bucket_policy(Bucket=bucket_name, Policy=json.dumps(bucket_policy))
        
        # Create CloudTrail
        cloudtrail.create_trail(
            Name='security-analysis-trail',
            S3BucketName=bucket_name
        )
        
        cloudtrail.start_logging(Name='security-analysis-trail')
        print(f"✅ CloudTrail fixed and enabled")
        return True
        
    except Exception as e:
        print(f"❌ CloudTrail fix failed: {e}")
        return False

def fix_config_rule():
    """Add a valid Config rule"""
    try:
        config = boto3.client('config')
        
        # Use a valid rule identifier
        config.put_config_rule(
            ConfigRule={
                'ConfigRuleName': 'encrypted-volumes',
                'Source': {
                    'Owner': 'AWS',
                    'SourceIdentifier': 'ENCRYPTED_VOLUMES'
                }
            }
        )
        print("✅ Config rule fixed: encrypted-volumes")
        return True
        
    except Exception as e:
        print(f"❌ Config rule fix failed: {e}")
        return False

if __name__ == "__main__":
    print("🔧 Fixing CloudTrail and Config issues...")
    fix_cloudtrail()
    fix_config_rule()
    print("✅ Fixes applied!")
