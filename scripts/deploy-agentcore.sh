#!/bin/bash

# Deploy Well-Architected Security MCP to AgentCore Runtime
# Usage: ./deploy-agentcore.sh

set -e

echo "🚀 Deploying Well-Architected Security MCP to AgentCore..."

# Step 1: Install AgentCore CLI (if not already installed)
echo "📦 Installing AgentCore CLI..."
pip install bedrock-agentcore-starter-toolkit

# Step 2: Configure AgentCore deployment
echo "⚙️ Configuring AgentCore deployment..."
agentcore configure --entrypoint well_architected_security_agentcore.py --non-interactive

# Step 3: Deploy to AgentCore
echo "☁️ Deploying to AgentCore Runtime..."
agentcore launch

# Step 4: Check deployment status
echo "📊 Checking deployment status..."
agentcore status

# Step 5: Test deployment
echo "🧪 Testing deployment..."
agentcore invoke '{"prompt": "What tools are available?"}'

echo "✅ Deployment complete!"
echo "🎯 Agent deployed and ready for security analysis"
