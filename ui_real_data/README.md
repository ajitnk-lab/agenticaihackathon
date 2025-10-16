# Real Data UI Development

This folder contains UI components that connect to REAL AgentCore agents with memory components.

## Real Data Sources
- **Security Agent**: Real AWS Inspector findings, Config compliance scores
- **Cost Agent**: Real Cost Explorer data for security services
- **Memory Integration**: Historical data and trend analysis from AgentCore Memory

## Files
- `dashboard_real.html` - Main dashboard with real data integration
- `backend_real.py` - Backend Lambda that calls real AgentCore agents
- `deploy_real.py` - Deployment script for real data UI

## Key Difference
Unlike the existing UI with static/mock data, this UI connects directly to:
- `src/agentcore/well_architected_security_agentcore.py` 
- `src/agentcore/cost_analysis_agentcore.py`
- Real AWS APIs (Inspector, Config, Cost Explorer)
