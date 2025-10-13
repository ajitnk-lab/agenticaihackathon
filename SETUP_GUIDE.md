# Project Setup Guide - Continue from Any Machine

## 🚀 Quick Start (New Machine Setup)

### Prerequisites
```bash
# Required software
- AWS CLI v2
- Node.js 18+
- Python 3.10+
- Git

# AWS Account Requirements
- Account ID: 039920874011
- Region: us-east-1
- Bedrock access enabled
- AgentCore access enabled
```

### 1. Clone Repository
```bash
git clone https://github.com/ajitnk-lab/agenticaihackathon.git
cd agenticaihackathon
```

### 2. Install Dependencies
```bash
# Node.js dependencies
npm install

# Python dependencies
pip install bedrock-agentcore-starter-toolkit boto3

# CDK CLI (if needed)
npm install -g aws-cdk
```

### 3. Configure AWS Credentials
```bash
aws configure
# Use your AWS credentials for account 039920874011
# Region: us-east-1
```

### 4. Verify Current Deployment Status
```bash
# Check if AgentCore agent is still deployed
agentcore status

# If agent exists, you should see:
# Agent Name: well_architected_security_agentcore
# Agent ARN: arn:aws:bedrock-agentcore:us-east-1:039920874011:runtime/well_architected_security_agentcore-uBgBoaAnRs
```

## 📋 Current Project Status (Day 2 Complete)

### ✅ Completed
- **Infrastructure**: CDK stack with VPC, DynamoDB, S3, CloudFront
- **MCP Server**: Well-Architected Security MCP deployed to AgentCore
- **Agent ARN**: `well_architected_security_agentcore-uBgBoaAnRs`
- **Tools Available**: `analyze_security_posture`, `get_security_findings`
- **Documentation**: Complete transformation guide in `MCP_TO_AGENTCORE_TRANSFORMATION.md`

### 🔄 Next Steps (Day 3)
- [ ] Implement Account Discovery MCP server
- [ ] Create Cost Analysis MCP server
- [ ] Build Report Generator MCP
- [ ] Test cross-account functionality

## 🔧 Key Files & Configurations

### Core Files
- `well_architected_security_agentcore.py` - Deployed AgentCore agent
- `deploy-agentcore.sh` - Deployment automation script
- `MCP_TO_AGENTCORE_TRANSFORMATION.md` - Complete documentation
- `TASKS.md` - Project timeline and progress

### Configuration Files (Local Only)
- `.bedrock_agentcore.yaml` - AgentCore config (auto-generated, gitignored)
- `.bedrock_agentcore/` - Deployment artifacts (auto-generated)

### Infrastructure
- CDK stack: `SecurityInfrastructureStack`
- DynamoDB: `security-orchestrator-findings`
- S3 buckets: Reports and web hosting
- CloudFront: Web distribution

## 🧪 Testing Current Deployment

### Test AgentCore Agent
```bash
# Basic functionality test
agentcore invoke '{"prompt": "What tools are available?"}'

# Security analysis test
agentcore invoke '{"prompt": "analyze_security_posture for account 123456789012"}'

# Security findings test
agentcore invoke '{"prompt": "get_security_findings for account 987654321098"}'
```

### Expected Responses
- Tools available: `analyze_security_posture`, `get_security_findings`
- Security analysis: JSON with security score, findings, recommendations
- Security findings: JSON with findings count, severity, top findings

## 🔄 If AgentCore Agent is Missing

### Redeploy from Scratch
```bash
# Use automation script
./deploy-agentcore.sh

# Or manual deployment
agentcore configure --entrypoint well_architected_security_agentcore.py --non-interactive
agentcore launch
agentcore status
```

## 📁 Project Structure
```
agenticaihackathon/
├── README.md                                    # Project overview
├── TASKS.md                                     # Timeline and progress
├── MCP_TO_AGENTCORE_TRANSFORMATION.md          # Day 2 documentation
├── SETUP_GUIDE.md                              # This file
├── deploy-agentcore.sh                         # Deployment automation
├── well_architected_security_agentcore.py      # AgentCore agent
├── requirements.txt                            # Python dependencies
├── package.json                                # Node.js dependencies
├── lib/security-infrastructure-stack.ts        # CDK infrastructure
├── mcp-servers/                                # MCP server source code
│   └── well-architected-security-mcp-server/   # Original MCP server
└── .bedrock_agentcore.yaml                     # AgentCore config (local)
```

## 🔐 Security Notes

### Sensitive Files (Not in Git)
- `.bedrock_agentcore.yaml` - Contains AWS ARNs and IDs
- AWS credentials - Configure locally
- Agent session data - Auto-managed by AgentCore

### Safe to Share
- All code files in repository
- Documentation and guides
- Deployment scripts
- Infrastructure definitions

## 🚨 Troubleshooting

### Common Issues
1. **AgentCore CLI not found**: `pip install bedrock-agentcore-starter-toolkit`
2. **AWS credentials**: Ensure account 039920874011 access
3. **Bedrock permissions**: Verify Bedrock and AgentCore access
4. **Agent not found**: Redeploy using `./deploy-agentcore.sh`

### Verification Commands
```bash
# Check AWS access
aws sts get-caller-identity

# Check Bedrock access
aws bedrock list-foundation-models --region us-east-1

# Check AgentCore CLI
agentcore --version

# Check current agents
agentcore status
```

## 📞 Support Resources

### Documentation
- `MCP_TO_AGENTCORE_TRANSFORMATION.md` - Complete transformation guide
- `TASKS.md` - Project timeline and next steps
- AWS AgentCore docs: https://docs.aws.amazon.com/bedrock-agentcore/

### Key Commands Reference
```bash
# AgentCore Management
agentcore configure --entrypoint <file> --non-interactive
agentcore launch
agentcore status
agentcore invoke '{"prompt": "..."}'

# CDK Management
cdk synth
cdk deploy --all
cdk destroy --all

# Git Management
git status
git add .
git commit -m "message"
git push origin main
```

---

**✅ With this guide, you can continue the project from any machine with full context and working deployment!**
