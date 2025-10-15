#!/bin/bash

# AgentCore Security Dashboard - Cleanup Script
set -e

PROJECT_NAME="agentcore-security-dashboard"
AWS_REGION="${AWS_REGION:-us-east-1}"
STACK_NAME="${PROJECT_NAME}-stack"

echo "🗑️  Destroying AgentCore Security Dashboard..."
echo "📍 Region: $AWS_REGION"
echo "📦 Stack: $STACK_NAME"

# Check AWS CLI
if ! command -v aws &> /dev/null; then
    echo "❌ AWS CLI not found"
    exit 1
fi

# Delete CloudFormation stack
echo "🗑️  Deleting CloudFormation stack..."
aws cloudformation delete-stack \
    --stack-name "$STACK_NAME" \
    --region "$AWS_REGION"

echo "⏳ Waiting for stack deletion to complete..."
aws cloudformation wait stack-delete-complete \
    --stack-name "$STACK_NAME" \
    --region "$AWS_REGION"

if [ $? -eq 0 ]; then
    echo "✅ Stack deleted successfully"
    echo "🧹 Cleanup complete!"
else
    echo "❌ Stack deletion failed or timed out"
    echo "💡 Check AWS Console for manual cleanup"
fi
