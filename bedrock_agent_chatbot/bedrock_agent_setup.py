#!/usr/bin/env python3
"""
Setup Bedrock Agent for proper orchestration
Creates or configures Bedrock Agent with Action Groups
"""

import boto3
import json
import time

def create_bedrock_agent():
    """Create Bedrock Agent with AgentCore Action Groups"""
    
    bedrock_agent = boto3.client('bedrock-agent', region_name='us-east-1')
    
    # Agent configuration
    agent_name = 'AgentCore-Security-Assistant'
    agent_description = 'AI assistant that orchestrates AgentCore Security and Cost agents for comprehensive security analysis'
    
    # Foundation model
    foundation_model = 'anthropic.claude-3-sonnet-20240229-v1:0'
    
    # Agent instructions
    instructions = """You are an AI security assistant that helps users analyze their AWS security posture and costs.

You have access to two specialized AgentCore agents:
1. Security Agent - Provides real AWS security findings, compliance data, and security scores
2. Cost Agent - Provides security service costs, ROI analysis, and investment recommendations

When users ask about security topics, call the appropriate agents and provide comprehensive, actionable insights.

Always:
- Use real data from the AgentCore agents
- Provide specific numbers and findings
- Explain security scores and ROI calculations
- Suggest actionable improvements
- Be conversational and helpful

Example responses:
- For security questions: Call Security Agent and explain findings with severity levels
- For cost questions: Call Cost Agent and provide detailed cost breakdowns
- For ROI questions: Call both agents and calculate return on investment"""

    try:
        # Create agent
        response = bedrock_agent.create_agent(
            agentName=agent_name,
            description=agent_description,
            foundationModel=foundation_model,
            instruction=instructions,
            idleSessionTTLInSeconds=1800  # 30 minutes
        )
        
        agent_id = response['agent']['agentId']
        print(f"✅ Created Bedrock Agent: {agent_name}")
        print(f"🆔 Agent ID: {agent_id}")
        
        # Wait for agent creation
        print("⏳ Waiting for agent creation...")
        time.sleep(5)
        
        # Create Action Groups
        create_action_groups(agent_id)
        
        # Prepare agent
        prepare_agent(agent_id)
        
        return agent_id
        
    except Exception as e:
        print(f"❌ Error creating Bedrock Agent: {e}")
        return None

def create_action_groups(agent_id):
    """Create Action Groups for AgentCore agents"""
    
    bedrock_agent = boto3.client('bedrock-agent', region_name='us-east-1')
    
    # Security Agent Action Group
    security_schema = {
        "openapi": "3.0.0",
        "info": {
            "title": "AgentCore Security Agent API",
            "version": "1.0.0",
            "description": "API for AgentCore Security Agent"
        },
        "paths": {
            "/analyze_security": {
                "post": {
                    "summary": "Analyze security posture",
                    "description": "Get comprehensive security analysis including findings, scores, and compliance data",
                    "operationId": "analyzeSecurityPosture",
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "account_id": {
                                            "type": "string",
                                            "description": "AWS account ID to analyze"
                                        }
                                    }
                                }
                            }
                        }
                    },
                    "responses": {
                        "200": {
                            "description": "Security analysis results",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "security_score": {"type": "number"},
                                            "total_findings": {"type": "number"},
                                            "critical_findings": {"type": "number"},
                                            "high_findings": {"type": "number"}
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    }
    
    # Cost Agent Action Group
    cost_schema = {
        "openapi": "3.0.0",
        "info": {
            "title": "AgentCore Cost Agent API",
            "version": "1.0.0",
            "description": "API for AgentCore Cost Agent"
        },
        "paths": {
            "/analyze_costs": {
                "post": {
                    "summary": "Analyze security costs",
                    "description": "Get security service costs, ROI analysis, and investment recommendations",
                    "operationId": "analyzeSecurityCosts",
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "account_id": {
                                            "type": "string",
                                            "description": "AWS account ID to analyze"
                                        }
                                    }
                                }
                            }
                        }
                    },
                    "responses": {
                        "200": {
                            "description": "Cost analysis results",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "total_monthly_cost": {"type": "number"},
                                            "service_count": {"type": "number"},
                                            "roi_percentage": {"type": "number"}
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    }
    
    try:
        # Create Security Action Group
        security_response = bedrock_agent.create_agent_action_group(
            agentId=agent_id,
            agentVersion='DRAFT',
            actionGroupName='SecurityAgent',
            description='AgentCore Security Agent for security posture analysis',
            actionGroupExecutor={
                'lambda': 'arn:aws:lambda:us-east-1:039920874011:function:agentcore-security-lambda'
            },
            apiSchema={
                'payload': json.dumps(security_schema)
            }
        )
        
        print("✅ Created Security Action Group")
        
        # Create Cost Action Group
        cost_response = bedrock_agent.create_agent_action_group(
            agentId=agent_id,
            agentVersion='DRAFT',
            actionGroupName='CostAgent',
            description='AgentCore Cost Agent for cost and ROI analysis',
            actionGroupExecutor={
                'lambda': 'arn:aws:lambda:us-east-1:039920874011:function:agentcore-cost-lambda'
            },
            apiSchema={
                'payload': json.dumps(cost_schema)
            }
        )
        
        print("✅ Created Cost Action Group")
        
    except Exception as e:
        print(f"⚠️ Error creating Action Groups: {e}")
        print("💡 Action Groups can be created manually in AWS Console")

def prepare_agent(agent_id):
    """Prepare agent for use"""
    
    bedrock_agent = boto3.client('bedrock-agent', region_name='us-east-1')
    
    try:
        # Prepare agent
        response = bedrock_agent.prepare_agent(agentId=agent_id)
        
        print("✅ Preparing Bedrock Agent...")
        print("⏳ This may take a few minutes...")
        
        # Wait for preparation
        max_attempts = 30
        for attempt in range(max_attempts):
            try:
                agent_response = bedrock_agent.get_agent(agentId=agent_id)
                status = agent_response['agent']['agentStatus']
                
                if status == 'PREPARED':
                    print("✅ Bedrock Agent is ready!")
                    break
                elif status == 'FAILED':
                    print("❌ Agent preparation failed")
                    break
                else:
                    print(f"⏳ Agent status: {status} (attempt {attempt + 1}/{max_attempts})")
                    time.sleep(10)
                    
            except Exception as e:
                print(f"⚠️ Error checking agent status: {e}")
                break
        
        # Create alias
        try:
            alias_response = bedrock_agent.create_agent_alias(
                agentId=agent_id,
                agentAliasName='prod',
                description='Production alias for AgentCore Security Assistant'
            )
            
            alias_id = alias_response['agentAlias']['agentAliasId']
            print(f"✅ Created agent alias: {alias_id}")
            
        except Exception as e:
            print(f"⚠️ Could not create alias: {e}")
            print("💡 Using default TSTALIASID alias")
        
    except Exception as e:
        print(f"❌ Error preparing agent: {e}")

def main():
    """Setup complete Bedrock Agent"""
    
    print("🤖 Setting up Bedrock Agent for AgentCore orchestration...")
    
    agent_id = create_bedrock_agent()
    
    if agent_id:
        print(f"\n🎉 Bedrock Agent Setup Complete!")
        print(f"🆔 Agent ID: {agent_id}")
        print("\n📋 Next steps:")
        print("1. Deploy the chatbot: python3 deploy_chatbot.py")
        print("2. Test the conversational interface")
        print("3. Ask natural language security questions")
        
        return agent_id
    else:
        print("❌ Bedrock Agent setup failed")
        return None

if __name__ == "__main__":
    main()
