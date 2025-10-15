#!/usr/bin/env python3
"""
Create Lambda execution role
"""

import boto3
import json

def create_lambda_role():
    """Create IAM role for Lambda execution"""
    iam = boto3.client('iam')
    
    # Trust policy for Lambda
    trust_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {
                    "Service": "lambda.amazonaws.com"
                },
                "Action": "sts:AssumeRole"
            }
        ]
    }
    
    try:
        # Create role
        response = iam.create_role(
            RoleName='lambda-execution-role',
            AssumeRolePolicyDocument=json.dumps(trust_policy),
            Description='Lambda execution role for security dashboard'
        )
        
        # Attach basic execution policy
        iam.attach_role_policy(
            RoleName='lambda-execution-role',
            PolicyArn='arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole'
        )
        
        print(f"✅ Created Lambda role: {response['Role']['Arn']}")
        return response['Role']['Arn']
        
    except iam.exceptions.EntityAlreadyExistsException:
        # Role already exists, get ARN
        response = iam.get_role(RoleName='lambda-execution-role')
        print(f"✅ Using existing Lambda role: {response['Role']['Arn']}")
        return response['Role']['Arn']
    except Exception as e:
        print(f"❌ Role creation failed: {e}")
        return None

if __name__ == "__main__":
    create_lambda_role()
