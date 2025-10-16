#!/usr/bin/env python3
"""
IAM Setup for AgentCore UI Dashboard
Creates required roles and permissions
"""

import boto3
import json

def create_lambda_execution_role():
    """Create IAM role for Lambda functions"""
    
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
    
    # Permissions policy
    permissions_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Action": [
                    "logs:CreateLogGroup",
                    "logs:CreateLogStream",
                    "logs:PutLogEvents"
                ],
                "Resource": "arn:aws:logs:*:*:*"
            },
            {
                "Effect": "Allow",
                "Action": [
                    "securityhub:GetFindings",
                    "config:GetComplianceSummaryByConfigRule",
                    "ce:GetCostAndUsage",
                    "inspector2:ListFindings",
                    "guardduty:ListFindings"
                ],
                "Resource": "*"
            }
        ]
    }
    
    role_name = 'lambda-execution-role'
    
    try:
        # Try to create role
        try:
            response = iam.create_role(
                RoleName=role_name,
                AssumeRolePolicyDocument=json.dumps(trust_policy),
                Description='Execution role for AgentCore UI Lambda functions'
            )
            print(f"✅ Created IAM role: {role_name}")
            
        except iam.exceptions.EntityAlreadyExistsException:
            print(f"✅ IAM role already exists: {role_name}")
        
        # Attach basic Lambda execution policy
        try:
            iam.attach_role_policy(
                RoleName=role_name,
                PolicyArn='arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole'
            )
        except:
            pass
        
        # Create and attach custom policy
        policy_name = 'AgentCoreUIPolicy'
        
        try:
            policy_response = iam.create_policy(
                PolicyName=policy_name,
                PolicyDocument=json.dumps(permissions_policy),
                Description='Custom policy for AgentCore UI Lambda functions'
            )
            policy_arn = policy_response['Policy']['Arn']
            print(f"✅ Created IAM policy: {policy_name}")
            
        except iam.exceptions.EntityAlreadyExistsException:
            # Get existing policy ARN
            account_id = boto3.client('sts').get_caller_identity()['Account']
            policy_arn = f"arn:aws:iam::{account_id}:policy/{policy_name}"
            print(f"✅ IAM policy already exists: {policy_name}")
        
        # Attach custom policy to role
        try:
            iam.attach_role_policy(
                RoleName=role_name,
                PolicyArn=policy_arn
            )
            print(f"✅ Attached policy to role")
        except:
            pass
        
        # Get role ARN
        role_response = iam.get_role(RoleName=role_name)
        role_arn = role_response['Role']['Arn']
        
        return role_arn
        
    except Exception as e:
        print(f"❌ IAM setup error: {e}")
        return None

def main():
    """Setup IAM roles and permissions"""
    
    print("🔐 Setting up IAM roles and permissions for AgentCore UI...")
    
    role_arn = create_lambda_execution_role()
    
    if role_arn:
        print(f"\n✅ IAM Setup Complete!")
        print(f"🔐 Role ARN: {role_arn}")
        print("\n📋 Permissions granted:")
        print("  • CloudWatch Logs (for Lambda logging)")
        print("  • Security Hub (for real security findings)")
        print("  • Config (for compliance data)")
        print("  • Cost Explorer (for cost analysis)")
        print("  • Inspector (for vulnerability data)")
        print("  • GuardDuty (for threat detection)")
    else:
        print("❌ IAM setup failed")

if __name__ == "__main__":
    main()
