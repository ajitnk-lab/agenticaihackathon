#!/usr/bin/env python3
"""
Deploy UI with CloudFront
"""

import boto3
import json
import time

def deploy_ui():
    """Deploy dashboard with CloudFront"""
    s3 = boto3.client('s3')
    cloudfront = boto3.client('cloudfront')
    
    bucket_name = f"security-dashboard-{int(time.time())}"
    
    try:
        # Create S3 bucket
        s3.create_bucket(Bucket=bucket_name)
        
        # Upload dashboard
        s3.upload_file(
            'dashboard_simple.html',
            bucket_name,
            'index.html',
            ExtraArgs={'ContentType': 'text/html'}
        )
        
        # Create CloudFront distribution
        distribution_config = {
            'CallerReference': str(int(time.time())),
            'Comment': 'Security Dashboard',
            'DefaultRootObject': 'index.html',
            'Origins': {
                'Quantity': 1,
                'Items': [
                    {
                        'Id': 'S3Origin',
                        'DomainName': f'{bucket_name}.s3.amazonaws.com',
                        'S3OriginConfig': {
                            'OriginAccessIdentity': ''
                        }
                    }
                ]
            },
            'DefaultCacheBehavior': {
                'TargetOriginId': 'S3Origin',
                'ViewerProtocolPolicy': 'redirect-to-https',
                'MinTTL': 0,
                'ForwardedValues': {
                    'QueryString': False,
                    'Cookies': {'Forward': 'none'}
                }
            },
            'Enabled': True
        }
        
        response = cloudfront.create_distribution(
            DistributionConfig=distribution_config
        )
        
        domain_name = response['Distribution']['DomainName']
        url = f"https://{domain_name}"
        
        print(f"✅ Dashboard deployed!")
        print(f"📊 URL: {url}")
        print(f"⏳ CloudFront deployment takes 5-15 minutes")
        
        return url
        
    except Exception as e:
        print(f"❌ Deployment failed: {e}")
        # Fallback to direct S3 URL
        s3_url = f"https://{bucket_name}.s3.amazonaws.com/index.html"
        print(f"📊 Fallback URL: {s3_url}")
        return s3_url

if __name__ == "__main__":
    deploy_ui()
