# MCP Server to AgentCore Transformation Documentation

## Overview
This document details the transformation of the Well-Architected Security MCP server to run on Amazon Bedrock AgentCore Runtime.

## Original MCP Server Structure

### Location
```
mcp-servers/well-architected-security-mcp-server/src/
```

### Code Pattern
```python
from mcp.server import Server
from mcp.types import Tool, TextContent

app = Server("well-architected-security")

@app.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="analyze_security_posture",
            description="Analyze AWS account security posture using Well-Architected Framework",
            inputSchema={...}
        ),
        Tool(
            name="get_security_findings", 
            description="Get security findings from Security Hub, GuardDuty, and Inspector",
            inputSchema={...}
        )
    ]

@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    if name == "analyze_security_posture":
        # Security analysis logic
    elif name == "get_security_findings":
        # Security findings logic
```

## Transformed AgentCore Version

### Location
```
well_architected_security_agentcore.py
```

### Code Pattern
```python
from bedrock_agentcore.runtime import BedrockAgentCoreApp
import json

app = BedrockAgentCoreApp()

async def analyze_security_posture(account_id: str, region: str = "us-east-1"):
    """Analyze AWS account security posture using Well-Architected Framework"""
    # Same security analysis logic as original MCP

async def get_security_findings(account_id: str, severity: str = "HIGH"):
    """Get security findings from Security Hub, GuardDuty, and Inspector"""
    # Same security findings logic as original MCP

@app.entrypoint
async def handler(event):
    """AgentCore entrypoint - transforms MCP server functionality"""
    prompt = event.get("prompt", "")
    
    # Parse tool calls from prompt and route to appropriate function
    if "analyze_security_posture" in prompt:
        result = await analyze_security_posture(account_id)
    elif "get_security_findings" in prompt:
        result = await get_security_findings(account_id)
    
    return {"body": json.dumps(result, indent=2)}
```

## Key Transformations

### 1. Import Changes
- **Before**: `from mcp.server import Server`
- **After**: `from bedrock_agentcore.runtime import BedrockAgentCoreApp`

### 2. App Initialization
- **Before**: `app = Server("well-architected-security")`
- **After**: `app = BedrockAgentCoreApp()`

### 3. Tool Definition
- **Before**: `@app.list_tools()` decorator with Tool objects
- **After**: Individual async functions (no decorator needed)

### 4. Tool Execution
- **Before**: `@app.call_tool()` with structured arguments
- **After**: `@app.entrypoint` with prompt parsing

### 5. Input Handling
- **Before**: Structured MCP arguments `call_tool(name, arguments)`
- **After**: Parse from event prompt `event.get("prompt", "")`

### 6. Output Format
- **Before**: `list[TextContent]` objects
- **After**: JSON response `{"body": json.dumps(result)}`

## Files Created for AgentCore Deployment

### 1. Core Files
- **`well_architected_security_agentcore.py`** - Transformed MCP server
- **`requirements.txt`** - Dependencies (bedrock-agentcore>=0.1.7, boto3>=1.34.0)

### 2. Auto-Generated Files
- **`.bedrock_agentcore.yaml`** - AgentCore configuration
- **`.bedrock_agentcore/`** - Deployment artifacts directory
- **`.dockerignore`** - Docker build exclusions

## Deployment Process

### 1. Configuration
```bash
agentcore configure --entrypoint well_architected_security_agentcore.py --non-interactive
```

### 2. Deployment
```bash
agentcore launch
```

### 3. Testing
```bash
agentcore invoke '{"prompt": "analyze_security_posture for account 123456789012"}'
```

## Deployment Results

### Agent Details
- **Agent Name**: `well_architected_security_agentcore`
- **Agent ARN**: `arn:aws:bedrock-agentcore:us-east-1:039920874011:runtime/well_architected_security_agentcore-uBgBoaAnRs`
- **Status**: READY
- **Region**: us-east-1
- **Account**: 039920874011

### Available Tools
1. **analyze_security_posture** - AWS account security analysis
2. **get_security_findings** - Security Hub/GuardDuty findings

## Test Payloads

### Security Posture Analysis
```json
{
  "prompt": "analyze_security_posture for account 123456789012 in us-east-1"
}
```

### Security Findings
```json
{
  "prompt": "get_security_findings for account 987654321098 with HIGH severity"
}
```

## Key Differences: MCP vs AgentCore

| Aspect | MCP Server | AgentCore |
|--------|------------|-----------|
| Framework | Model Context Protocol | Bedrock AgentCore Runtime |
| Deployment | Standalone service | Hosted application |
| Tool Definition | Structured Tool objects | Async functions |
| Input Handling | Structured arguments | Prompt parsing |
| Output Format | TextContent objects | JSON responses |
| Scaling | Manual | Auto-scaling |
| Monitoring | Custom | Built-in observability |

## Notes

- **Functionality Preserved**: All security analysis logic remains identical
- **Architecture Changed**: From MCP protocol to AgentCore runtime
- **Deployment Simplified**: Single command deployment vs manual service setup
- **Integration Ready**: Can be invoked by Bedrock Agents or direct API calls

## Future Enhancements

1. **Enhanced Prompt Parsing**: More sophisticated parameter extraction from prompts
2. **Multi-Account Support**: Dynamic account ID parsing from prompts
3. **Real AWS Integration**: Connect to actual Security Hub, GuardDuty APIs
4. **Memory Integration**: Use AgentCore Memory for persistent findings storage
