# Security ROI Calculator - AWS AI Agent Hackathon 2025

AI-powered security orchestration architecture demonstrating how Bedrock Agent can coordinate multiple analysis agents for security ROI calculation.

## 🎯 **What This Demonstrates**
- **AI Orchestration**: Bedrock Agent coordinating multiple specialized analysis agents
- **Multi-MCP Integration**: AgentCore runtimes working together for complex workflows  
- **Security ROI Analysis**: Mock workflow showing how to analyze security spending vs. security achievement
- **Scalable Architecture**: Foundation for real multi-account security analysis

## 🚨 **Important: Demo Architecture Only**
This is a **proof-of-concept** showing AI orchestration capabilities with mock data. It does not:
- Access real multi-account AWS data (no cross-account IAM roles)
- Provide genuine security analysis (all findings are hardcoded)
- Calculate actual ROI (all costs are mock values)

## 📁 **Project Structure**
```
├── src/
│   ├── agentcore/          # AgentCore runtime implementations
│   └── lambda/             # Lambda function for Bedrock Agent integration
├── tests/                  # Test scripts and demo examples
├── scripts/                # Deployment and setup scripts
├── docs/                   # Documentation and project details
├── lib/                    # CDK infrastructure code
└── mcp-servers/           # MCP server configurations
```

## 🚀 **Quick Start**

### 1. Deploy AgentCore Runtimes
```bash
cd src/agentcore
agentcore deploy cost_analysis_agentcore.py
agentcore deploy well_architected_security_agentcore.py
```

### 2. Deploy Lambda Function
```bash
cd scripts
python3 deploy_lambda.py
```

### 3. Test Multi-Account Analysis
```bash
cd tests
python3 test_multi_account.py single
python3 test_multi_account.py org
```

## 🏆 **Hackathon Value**
Demonstrates novel AI orchestration approach where Bedrock Agent coordinates multiple specialized agents for complex security analysis workflows.

## 📚 **Documentation**
- [Project Details](docs/PROJECT_README.md)
- [Architecture](docs/ARCHITECTURE.md) 
- [Setup Guide](docs/SETUP_GUIDE.md)
- [Tasks Status](docs/TASKS.md)

**Status: Demo Architecture Ready for Hackathon Submission**
