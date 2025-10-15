#!/usr/bin/env python3
"""Create Bedrock Agent with correct configuration"""

import boto3
import json
import time

def create_agent():
    bedrock_agent = boto3.client('bedrock-agent', region_name='us-east-1')
    
    agent_id = 'C6ZC4AGYNQ'  # Use existing agent
    print(f"Using agent: {agent_id}")
    
    # Create action group with API schema (not function schema)
    api_schema = {
        "openapi": "3.0.0",
        "info": {
            "title": "Security Analysis API",
            "version": "1.0.0"
        },
        "paths": {
            "/analyze": {
                "post": {
                    "description": "Analyze security posture",
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "account_id": {
                                            "type": "string",
                                            "description": "AWS account ID"
                                        }
                                    },
                                    "required": ["account_id"]
                                }
                            }
                        }
                    },
                    "responses": {
                        "200": {
                            "description": "Security analysis results",
                            "content": {
                                "application/json": {
                                    "schema": {"type": "object"}
                                }
                            }
                        }
                    }
                }
            }
        }
    }
    
    action_group_response = bedrock_agent.create_agent_action_group(
        agentId=agent_id,
        agentVersion='DRAFT',
        actionGroupName='SecurityActions',
        description='Security analysis actions',
        actionGroupExecutor={
            'lambda': 'arn:aws:lambda:us-east-1:039920874011:function:security-orchestrator-bedrock-agent'
        },
        apiSchema={
            'payload': json.dumps(api_schema)
        },
        actionGroupState='ENABLED'
    )
    
    print(f"Created action group: {action_group_response['agentActionGroup']['actionGroupId']}")
    
    # Prepare agent
    bedrock_agent.prepare_agent(agentId=agent_id)
    print(f"Preparing agent...")
    
    return agent_id

if __name__ == "__main__":
    agent_id = create_agent()
    print(f"Agent ID: {agent_id}")
