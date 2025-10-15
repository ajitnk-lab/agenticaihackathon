#!/usr/bin/env python3

import boto3
import json
import time

def create_agent_with_api_schema():
    """Create a new Bedrock Agent with the updated API schema"""
    
    bedrock_agent = boto3.client('bedrock-agent', region_name='us-east-1')
    
    # Load the API schema
    with open('updated_api_schema.json', 'r') as f:
        api_schema = json.load(f)
    
    try:
        # Create the agent with role ARN
        print("Creating Bedrock Agent...")
        agent_response = bedrock_agent.create_agent(
            agentName='SecurityROICalculatorUpdated',
            agentResourceRoleArn='arn:aws:iam::039920874011:role/BedrockAgentRole',
            description='AI agent for analyzing security posture and calculating ROI for AWS accounts',
            foundationModel='anthropic.claude-3-sonnet-20240229-v1:0',
            instruction='You are a security analysis expert. Help users analyze their AWS security posture and calculate ROI for security investments. Use the analyze_security function to get detailed security analysis and cost information.',
            idleSessionTTLInSeconds=1800
        )
        
        agent_id = agent_response['agent']['agentId']
        print(f"Agent created with ID: {agent_id}")
        
        # Wait for agent to be ready
        print("Waiting for agent to be ready...")
        time.sleep(10)
        
        # Create action group with API schema
        print("Creating action group with API schema...")
        action_group_response = bedrock_agent.create_agent_action_group(
            agentId=agent_id,
            agentVersion='DRAFT',
            actionGroupName='SecurityAnalysisActions',
            description='Actions for security analysis and ROI calculation',
            actionGroupExecutor={
                'lambda': 'arn:aws:lambda:us-east-1:039920874011:function:security-orchestrator-lambda'
            },
            apiSchema={
                'payload': json.dumps(api_schema)
            },
            actionGroupState='ENABLED'
        )
        
        print(f"Action group created: {action_group_response['agentActionGroup']['actionGroupName']}")
        
        # Prepare the agent
        print("Preparing agent...")
        prepare_response = bedrock_agent.prepare_agent(agentId=agent_id)
        print(f"Agent preparation status: {prepare_response['agentStatus']}")
        
        # Wait for preparation to complete
        print("Waiting for agent preparation to complete...")
        while True:
            agent_status = bedrock_agent.get_agent(agentId=agent_id)
            status = agent_status['agent']['agentStatus']
            print(f"Current status: {status}")
            
            if status == 'PREPARED':
                break
            elif status == 'FAILED':
                print("Agent preparation failed!")
                return None
            
            time.sleep(10)
        
        # Create agent alias
        print("Creating agent alias...")
        alias_response = bedrock_agent.create_agent_alias(
            agentId=agent_id,
            agentAliasName='prod',
            description='Production alias for Security ROI Calculator'
        )
        
        alias_id = alias_response['agentAlias']['agentAliasId']
        print(f"Agent alias created: {alias_id}")
        
        print(f"\n✅ Agent setup complete!")
        print(f"Agent ID: {agent_id}")
        print(f"Alias ID: {alias_id}")
        
        return agent_id, alias_id
        
    except Exception as e:
        print(f"Error creating agent: {str(e)}")
        return None

if __name__ == "__main__":
    create_agent_with_api_schema()
