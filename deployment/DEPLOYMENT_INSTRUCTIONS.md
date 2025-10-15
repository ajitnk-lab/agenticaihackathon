# AgentCore Deployment Instructions

## Files to Deploy:
1. well_architected_security_comprehensive.py (main runtime)
2. .bedrock_agentcore.yaml (configuration)

## Deployment Steps:
1. Upload both files to your AgentCore environment
2. Ensure AWS credentials are configured
3. Deploy using AgentCore CLI or console
4. Test with the available tools

## Available Tools:
- check_security_services
- get_security_findings  
- check_storage_encryption
- check_network_security
- comprehensive_analysis

## Test Command:
python3 test_comprehensive_security.py
