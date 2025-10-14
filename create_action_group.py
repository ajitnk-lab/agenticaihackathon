#!/usr/bin/env python3
import boto3
import json

def create_action_group():
    client = boto3.client('bedrock-agent', region_name='us-east-1')
    
    # Minimal OpenAPI schema
    schema = {
        "openapi": "3.0.0",
        "info": {
            "title": "Security API",
            "version": "1.0.0"
        },
        "paths": {
            "/analyze_security_posture": {
                "post": {
                    "summary": "Analyze security posture",
                    "operationId": "analyzeSecurityPosture",
                    "requestBody": {
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "account_id": {"type": "string"}
                                    }
                                }
                            }
                        }
                    },
                    "responses": {
                        "200": {
                            "description": "Success",
                            "content": {
                                "application/json": {
                                    "schema": {"type": "object"}
                                }
                            }
                        }
                    }
                }
            },
            "/get_security_costs": {
                "post": {
                    "summary": "Get security costs",
                    "operationId": "getSecurityCosts",
                    "requestBody": {
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "account_id": {"type": "string"}
                                    }
                                }
                            }
                        }
                    },
                    "responses": {
                        "200": {
                            "description": "Success",
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
    
    try:
        response = client.create_agent_action_group(
            agentId='LKQIWEYEMZ',
            agentVersion='DRAFT',
            actionGroupName='SecurityAnalysisActions',
            description='Security analysis and cost optimization actions',
            actionGroupExecutor={
                'lambda': 'arn:aws:lambda:us-east-1:039920874011:function:security-orchestrator-bedrock-agent'
            },
            apiSchema={
                'payload': json.dumps(schema)
            }
        )
        print(f"Action group created: {response['agentActionGroup']['actionGroupId']}")
        return response
    except Exception as e:
        print(f"Error creating action group: {e}")
        return None

if __name__ == "__main__":
    create_action_group()
