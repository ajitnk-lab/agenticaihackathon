#!/usr/bin/env python3
"""Setup IAM roles and permissions for Security ROI Calculator"""

import boto3
import json

def create_lambda_role():
    """Create IAM role for Lambda function"""
    
    iam = boto3.client('iam')
    
    # Trust policy for Lambda
    trust_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {"Service": "lambda.amazonaws.com"},
                "Action": "sts:AssumeRole"
            }
        ]
    }
    
    # Permission policy
    permission_policy = {
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
                    "bedrock:InvokeModel",
                    "bedrock:InvokeModelWithResponseStream"
                ],
                "Resource": "*"
            }
        ]
    }
    
    try:
        # Create role
        role_response = iam.create_role(
            RoleName='SecurityROILambdaRole',
            AssumeRolePolicyDocument=json.dumps(trust_policy),
            Description='Role for Security ROI Calculator Lambda function'
        )
        
        # Attach basic execution policy
        iam.attach_role_policy(
            RoleName='SecurityROILambdaRole',
            PolicyArn='arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole'
        )
        
        # Create and attach custom policy
        policy_response = iam.create_policy(
            PolicyName='SecurityROILambdaPolicy',
            PolicyDocument=json.dumps(permission_policy),
            Description='Custom policy for Security ROI Calculator Lambda'
        )
        
        iam.attach_role_policy(
            RoleName='SecurityROILambdaRole',
            PolicyArn=policy_response['Policy']['Arn']
        )
        
        print(f"✅ Created Lambda role: {role_response['Role']['Arn']}")
        return role_response['Role']['Arn']
        
    except Exception as e:
        print(f"❌ Lambda role creation failed: {e}")
        return None

def create_bedrock_agent_role():
    """Create IAM role for Bedrock Agent"""
    
    iam = boto3.client('iam')
    
    # Trust policy for Bedrock
    trust_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {"Service": "bedrock.amazonaws.com"},
                "Action": "sts:AssumeRole"
            }
        ]
    }
    
    # Permission policy
    permission_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Action": [
                    "bedrock:InvokeModel",
                    "bedrock:InvokeModelWithResponseStream"
                ],
                "Resource": "*"
            },
            {
                "Effect": "Allow",
                "Action": "lambda:InvokeFunction",
                "Resource": "arn:aws:lambda:*:*:function:security-roi-orchestrator"
            }
        ]
    }
    
    try:
        # Create role
        role_response = iam.create_role(
            RoleName='SecurityROIBedrockAgentRole',
            AssumeRolePolicyDocument=json.dumps(trust_policy),
            Description='Role for Security ROI Calculator Bedrock Agent'
        )
        
        # Create and attach custom policy
        policy_response = iam.create_policy(
            PolicyName='SecurityROIBedrockAgentPolicy',
            PolicyDocument=json.dumps(permission_policy),
            Description='Custom policy for Security ROI Calculator Bedrock Agent'
        )
        
        iam.attach_role_policy(
            RoleName='SecurityROIBedrockAgentRole',
            PolicyArn=policy_response['Policy']['Arn']
        )
        
        print(f"✅ Created Bedrock Agent role: {role_response['Role']['Arn']}")
        return role_response['Role']['Arn']
        
    except Exception as e:
        print(f"❌ Bedrock Agent role creation failed: {e}")
        return None

def validate_permissions():
    """Validate current AWS permissions"""
    
    print("🔍 Validating AWS permissions...")
    
    try:
        # Test basic AWS access
        sts = boto3.client('sts')
        identity = sts.get_caller_identity()
        print(f"✅ AWS Identity: {identity.get('Arn', 'Unknown')}")
        
        # Test required services
        services = ['iam', 'lambda', 'bedrock-agent']
        
        for service in services:
            try:
                client = boto3.client(service)
                print(f"✅ {service.upper()} client created successfully")
            except Exception as e:
                print(f"❌ {service.upper()} access failed: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Permission validation failed: {e}")
        return False

if __name__ == "__main__":
    print("🔐 Setting up IAM roles for Security ROI Calculator...")
    
    if validate_permissions():
        print("\n💡 AWS permissions validated!")
        print("💡 To create IAM roles, ensure you have admin permissions")
        print("💡 Uncomment the role creation calls below")
        
        # Uncomment to create actual roles
        # lambda_role_arn = create_lambda_role()
        # bedrock_role_arn = create_bedrock_agent_role()
    else:
        print("❌ Permission validation failed")
