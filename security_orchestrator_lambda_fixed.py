import json
import boto3
import os

def lambda_handler(event, context):
    """Lambda function for Bedrock Agent security orchestration"""
    
    try:
        print(f"Event: {event}")
        
        # Extract Bedrock Agent event details
        action_group = event.get('actionGroup', '')
        api_path = event.get('apiPath', '')
        http_method = event.get('httpMethod', 'GET')
        input_text = event.get('inputText', '')
        
        # Extract account ID from context or use default
        account_id = context.invoked_function_arn.split(':')[4] if context else '039920874011'
        
        print(f"Function: {api_path}, Account: {account_id}")
        
        # Route to appropriate AgentCore runtime with specific tool calls
        if api_path == '/analyze_security':
            agent_arn = os.getenv('SECURITY_AGENT_ARN')
            result = call_agentcore(agent_arn, f"analyze_security_posture for account {account_id}", account_id)
        elif api_path == '/calculate_roi':
            agent_arn = os.getenv('COST_AGENT_ARN')
            result = call_agentcore(agent_arn, f"calculate_security_roi for account {account_id}", account_id)
        else:
            result = {"error": f"Unknown API path: {api_path}"}
        
        # Return proper Bedrock Agent response format
        return {
            'messageVersion': '1.0',
            'response': {
                'actionGroup': action_group,
                'apiPath': api_path,
                'httpMethod': http_method,
                'httpStatusCode': 200,
                'responseBody': {
                    'application/json': {
                        'body': json.dumps(result)
                    }
                }
            }
        }
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            'messageVersion': '1.0',
            'response': {
                'actionGroup': event.get('actionGroup', ''),
                'apiPath': event.get('apiPath', ''),
                'httpMethod': event.get('httpMethod', 'GET'),
                'httpStatusCode': 500,
                'responseBody': {
                    'application/json': {
                        'body': json.dumps({"error": str(e)})
                    }
                }
            }
        }

def call_agentcore(agent_arn, tool_prompt, account_id):
    """Call AgentCore runtime"""
    
    print(f"Calling AgentCore: {agent_arn}")
    
    try:
        client = boto3.client('bedrock-agentcore')
        
        # Call AgentCore with proper parameter structure and tool execution
        response = client.invoke_agent_runtime(
            agentRuntimeArn=agent_arn,
            payload=json.dumps({
                "inputText": tool_prompt,
                "account_id": account_id
            })
        )
        
        print(f"Response keys: {response.keys()}")
        
        # Parse AgentCore response - handle StreamingBody
        if 'body' in response:
            response_text = response['body']
            if hasattr(response_text, 'read'):
                response_text = response_text.read().decode('utf-8')
        elif 'response' in response:
            response_text = response['response']
            if hasattr(response_text, 'read'):
                response_text = response_text.read().decode('utf-8')
        elif 'payload' in response:
            response_text = response['payload']
            if hasattr(response_text, 'read'):
                response_text = response_text.read().decode('utf-8')
        else:
            print(f"Full response: {response}")
            return {"error": "Unexpected response format from AgentCore"}
        
        try:
            return json.loads(response_text)
        except json.JSONDecodeError:
            return {"response": response_text}
            
    except Exception as e:
        print(f"AgentCore call failed: {str(e)}")
        return {"error": f"AgentCore call failed: {str(e)}"}
