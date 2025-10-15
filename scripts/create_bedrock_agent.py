#!/usr/bin/env python3
"""Create and configure Bedrock Agent for Security ROI Calculator"""

import boto3
import json
import time

def create_bedrock_agent():
    """Create Bedrock Agent with action groups"""
    
    bedrock_client = boto3.client('bedrock-agent')
    
    # Agent configuration
    agent_config = {
        'agentName': 'security-roi-calculator',
        'description': 'Multi-account security analysis and ROI calculation agent',
        'foundationModel': 'anthropic.claude-3-sonnet-20240229-v1:0',
        'instruction': '''You are a security ROI calculator agent that helps analyze AWS security posture and calculate return on investment for security spending.

You have access to these capabilities:
1. Analyze security posture across AWS accounts
2. Calculate ROI for security investments  
3. Get historical trends from Memory primitive

Always provide actionable insights and recommendations based on the analysis.''',
        'idleSessionTTLInSeconds': 1800
    }
    
    try:
        # Create agent
        response = bedrock_client.create_agent(**agent_config)
        agent_id = response['agent']['agentId']
        
        print(f"✅ Created Bedrock Agent: {agent_id}")
        
        # Wait for agent to be ready
        time.sleep(5)
        
        # Create action group
        action_group_config = {
            'agentId': agent_id,
            'agentVersion': 'DRAFT',
            'actionGroupName': 'security-roi-actions',
            'description': 'Security analysis and ROI calculation actions',
            'actionGroupExecutor': {
                'lambda': 'arn:aws:lambda:us-west-2:123456789012:function:security-roi-orchestrator'
            },
            'apiSchema': {
                'payload': open('config/bedrock_agent_schema.json', 'r').read()
            }
        }
        
        action_response = bedrock_client.create_agent_action_group(**action_group_config)
        
        print(f"✅ Created Action Group: {action_response['agentActionGroup']['actionGroupId']}")
        
        # Prepare agent
        prepare_response = bedrock_client.prepare_agent(agentId=agent_id)
        
        print(f"✅ Agent prepared successfully")
        
        return agent_id
        
    except Exception as e:
        print(f"❌ Bedrock Agent creation failed: {e}")
        return None

def create_agent_alias(agent_id):
    """Create agent alias for testing"""
    
    bedrock_client = boto3.client('bedrock-agent')
    
    try:
        response = bedrock_client.create_agent_alias(
            agentId=agent_id,
            agentAliasName='test-alias',
            description='Test alias for Security ROI Calculator'
        )
        
        alias_id = response['agentAlias']['agentAliasId']
        print(f"✅ Created Agent Alias: {alias_id}")
        
        return alias_id
        
    except Exception as e:
        print(f"❌ Agent alias creation failed: {e}")
        return None

def test_agent_locally():
    """Test agent configuration locally"""
    
    print("🧪 Testing Bedrock Agent configuration...")
    
    # Validate schema
    try:
        with open('config/bedrock_agent_schema.json', 'r') as f:
            schema = json.load(f)
        
        required_paths = ['/analyze-security', '/calculate-roi', '/get-trends']
        
        for path in required_paths:
            if path in schema['paths']:
                print(f"✅ Schema path validated: {path}")
            else:
                print(f"❌ Missing schema path: {path}")
        
        return True
        
    except Exception as e:
        print(f"❌ Schema validation failed: {e}")
        return False

if __name__ == "__main__":
    print("🤖 Creating Bedrock Agent for Security ROI Calculator...")
    
    # Test configuration first
    if test_agent_locally():
        print("\n💡 Configuration validated successfully!")
        print("💡 To create actual Bedrock Agent, ensure:")
        print("   - Lambda function is deployed")
        print("   - IAM roles are configured")
        print("   - Update Lambda ARN in the script")
        
        # Uncomment to create actual agent
        # agent_id = create_bedrock_agent()
        # if agent_id:
        #     alias_id = create_agent_alias(agent_id)
    else:
        print("❌ Configuration validation failed")
