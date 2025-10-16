# Bedrock Agent Chatbot UI

This folder contains the chatbot UI that implements the proper Bedrock Agent orchestration flow.

## Architecture Flow

```
Chatbot UI → Bedrock Agent → Action Groups → AgentCore Runtimes → AWS APIs
```

## Features

- Natural language security queries
- Bedrock Agent orchestration
- Multi-agent coordination (Security + Cost agents)
- Conversational interface
- Real-time responses from AgentCore Memory

## Files

- `chatbot.html` - Chatbot UI interface
- `bedrock_agent_backend.py` - Backend that calls Bedrock Agent
- `deploy_chatbot.py` - Deployment script
- `bedrock_agent_setup.py` - Bedrock Agent configuration

## Usage

Users can ask natural language questions like:
- "What's my current security posture?"
- "Show me security ROI analysis"
- "What are my critical security findings?"
- "How much am I spending on security services?"

The Bedrock Agent will orchestrate calls to appropriate AgentCore agents and provide comprehensive responses.
