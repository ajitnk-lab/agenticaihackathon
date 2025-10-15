#!/usr/bin/env python3
"""
Final UI deployment - S3 only
"""

import boto3
import json

def deploy_to_s3():
    """Deploy dashboard to S3"""
    s3 = boto3.client('s3')
    bucket_name = 'security-dashboard-ui-final'
    
    try:
        # Create bucket
        s3.create_bucket(Bucket=bucket_name)
        
        # Upload HTML
        s3.upload_file(
            'dashboard_simple.html',
            bucket_name,
            'index.html',
            ExtraArgs={'ContentType': 'text/html'}
        )
        
        # Make bucket public
        bucket_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Sid": "PublicReadGetObject",
                    "Effect": "Allow",
                    "Principal": "*",
                    "Action": "s3:GetObject",
                    "Resource": f"arn:aws:s3:::{bucket_name}/*"
                }
            ]
        }
        
        s3.put_bucket_policy(
            Bucket=bucket_name,
            Policy=json.dumps(bucket_policy)
        )
        
        # Enable website hosting
        s3.put_bucket_website(
            Bucket=bucket_name,
            WebsiteConfiguration={
                'IndexDocument': {'Suffix': 'index.html'}
            }
        )
        
        url = f"http://{bucket_name}.s3-website-us-east-1.amazonaws.com"
        print(f"✅ Dashboard deployed: {url}")
        return url
        
    except Exception as e:
        print(f"❌ Deployment failed: {e}")
        return None

if __name__ == "__main__":
    deploy_to_s3()
