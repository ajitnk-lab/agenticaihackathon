#!/usr/bin/env python3
import boto3
import json
import time

def deploy():
    s3 = boto3.client('s3')
    bucket = f"dashboard-{int(time.time())}"
    
    # Create bucket
    s3.create_bucket(Bucket=bucket)
    
    # Upload with public read
    s3.put_object(
        Bucket=bucket,
        Key='index.html',
        Body=open('dashboard_standalone.html', 'rb'),
        ContentType='text/html'
    )
    
    # Public policy
    policy = {
        "Version": "2012-10-17",
        "Statement": [{
            "Effect": "Allow",
            "Principal": "*",
            "Action": "s3:GetObject",
            "Resource": f"arn:aws:s3:::{bucket}/*"
        }]
    }
    
    try:
        s3.put_bucket_policy(Bucket=bucket, Policy=json.dumps(policy))
        s3.put_bucket_website(
            Bucket=bucket,
            WebsiteConfiguration={'IndexDocument': {'Suffix': 'index.html'}}
        )
        url = f"http://{bucket}.s3-website-us-east-1.amazonaws.com"
    except:
        url = f"https://{bucket}.s3.amazonaws.com/index.html"
    
    print(f"✅ Deployed: {url}")
    return url

if __name__ == "__main__":
    deploy()
