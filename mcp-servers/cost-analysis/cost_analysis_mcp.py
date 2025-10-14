#!/usr/bin/env python3
"""
Cost Analysis MCP Server for Multi-Account AWS Security Orchestrator
Provides cost analysis and ROI calculations for security recommendations
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import boto3
from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import (
    Resource,
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource,
    LoggingLevel
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("cost-analysis-mcp")

class CostAnalysisMCP:
    def __init__(self):
        self.cost_explorer = boto3.client('ce')
        self.pricing = boto3.client('pricing', region_name='us-east-1')
        
        # Security services for cost analysis
        self.security_services = [
            'Amazon GuardDuty',
            'AWS Security Hub',
            'Amazon Inspector',
            'AWS Config',
            'AWS CloudTrail',
            'AWS WAF',
            'AWS Shield',
            'Amazon Macie',
            'AWS Systems Manager'
        ]

    async def get_security_costs(self, account_id: str, days: int = 30) -> Dict[str, Any]:
        """Get current security service costs for an account"""
        try:
            end_date = datetime.now().date()
            start_date = end_date - timedelta(days=days)
            
            response = self.cost_explorer.get_cost_and_usage(
                TimePeriod={
                    'Start': start_date.strftime('%Y-%m-%d'),
                    'End': end_date.strftime('%Y-%m-%d')
                },
                Granularity='MONTHLY',
                Metrics=['BlendedCost'],
                GroupBy=[
                    {'Type': 'DIMENSION', 'Key': 'SERVICE'}
                ],
                Filter={
                    'And': [
                        {
                            'Dimensions': {
                                'Key': 'LINKED_ACCOUNT',
                                'Values': [account_id]
                            }
                        },
                        {
                            'Dimensions': {
                                'Key': 'SERVICE',
                                'Values': self.security_services
                            }
                        }
                    ]
                }
            )
            
            costs = {}
            total_cost = 0
            
            for result in response['ResultsByTime']:
                for group in result['Groups']:
                    service = group['Keys'][0]
                    cost = float(group['Metrics']['BlendedCost']['Amount'])
                    costs[service] = cost
                    total_cost += cost
            
            return {
                'account_id': account_id,
                'period_days': days,
                'total_security_cost': round(total_cost, 2),
                'service_costs': costs,
                'currency': 'USD'
            }
            
        except Exception as e:
            logger.error(f"Error getting security costs: {str(e)}")
            return {'error': str(e)}

    async def estimate_recommendation_cost(self, recommendation: Dict[str, Any]) -> Dict[str, Any]:
        """Estimate cost impact of security recommendations"""
        try:
            service = recommendation.get('service', '')
            action = recommendation.get('action', '')
            accounts = recommendation.get('accounts', [])
            
            # Cost estimates for common security recommendations
            cost_estimates = {
                'GuardDuty': {
                    'enable': 2.50,  # per account per month
                    'threat_intelligence': 0.60  # per million events
                },
                'Security Hub': {
                    'enable': 0.0030,  # per finding per month
                    'compliance_checks': 0.001  # per check per month
                },
                'Config': {
                    'enable': 0.003,  # per configuration item
                    'rules': 0.001  # per rule evaluation
                },
                'Inspector': {
                    'enable': 0.09,  # per agent per month
                    'network_assessment': 0.50  # per assessment
                }
            }
            
            base_cost = cost_estimates.get(service, {}).get(action, 0)
            monthly_cost = base_cost * len(accounts)
            annual_cost = monthly_cost * 12
            
            # Calculate potential savings (breach prevention)
            risk_reduction = recommendation.get('risk_reduction', 0.1)
            avg_breach_cost = 4500000  # $4.5M average breach cost
            potential_savings = avg_breach_cost * risk_reduction
            
            roi_months = annual_cost / (potential_savings / 12) if potential_savings > 0 else float('inf')
            
            return {
                'recommendation': recommendation,
                'cost_estimate': {
                    'monthly_cost': round(monthly_cost, 2),
                    'annual_cost': round(annual_cost, 2),
                    'currency': 'USD'
                },
                'roi_analysis': {
                    'potential_annual_savings': round(potential_savings, 2),
                    'payback_period_months': round(roi_months, 1) if roi_months != float('inf') else 'N/A',
                    'roi_percentage': round((potential_savings - annual_cost) / annual_cost * 100, 1) if annual_cost > 0 else 'N/A'
                }
            }
            
        except Exception as e:
            logger.error(f"Error estimating recommendation cost: {str(e)}")
            return {'error': str(e)}

    async def calculate_security_roi(self, investments: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate ROI for security investments"""
        try:
            total_investment = 0
            total_savings = 0
            
            for investment in investments:
                cost = investment.get('annual_cost', 0)
                savings = investment.get('potential_savings', 0)
                total_investment += cost
                total_savings += savings
            
            net_benefit = total_savings - total_investment
            roi_percentage = (net_benefit / total_investment * 100) if total_investment > 0 else 0
            
            return {
                'total_annual_investment': round(total_investment, 2),
                'total_potential_savings': round(total_savings, 2),
                'net_annual_benefit': round(net_benefit, 2),
                'roi_percentage': round(roi_percentage, 1),
                'payback_period_months': round(total_investment / (total_savings / 12), 1) if total_savings > 0 else 'N/A',
                'currency': 'USD'
            }
            
        except Exception as e:
            logger.error(f"Error calculating security ROI: {str(e)}")
            return {'error': str(e)}

    async def get_cost_trends(self, account_ids: List[str], months: int = 12) -> Dict[str, Any]:
        """Get historical security spending trends"""
        try:
            end_date = datetime.now().date()
            start_date = end_date - timedelta(days=months * 30)
            
            response = self.cost_explorer.get_cost_and_usage(
                TimePeriod={
                    'Start': start_date.strftime('%Y-%m-%d'),
                    'End': end_date.strftime('%Y-%m-%d')
                },
                Granularity='MONTHLY',
                Metrics=['BlendedCost'],
                GroupBy=[
                    {'Type': 'DIMENSION', 'Key': 'LINKED_ACCOUNT'}
                ],
                Filter={
                    'And': [
                        {
                            'Dimensions': {
                                'Key': 'LINKED_ACCOUNT',
                                'Values': account_ids
                            }
                        },
                        {
                            'Dimensions': {
                                'Key': 'SERVICE',
                                'Values': self.security_services
                            }
                        }
                    ]
                }
            )
            
            trends = []
            for result in response['ResultsByTime']:
                month_data = {
                    'month': result['TimePeriod']['Start'],
                    'accounts': {}
                }
                
                for group in result['Groups']:
                    account_id = group['Keys'][0]
                    cost = float(group['Metrics']['BlendedCost']['Amount'])
                    month_data['accounts'][account_id] = cost
                
                trends.append(month_data)
            
            return {
                'period_months': months,
                'trends': trends,
                'currency': 'USD'
            }
            
        except Exception as e:
            logger.error(f"Error getting cost trends: {str(e)}")
            return {'error': str(e)}

    async def optimize_security_budget(self, budget: float, recommendations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Optimize security recommendations within budget constraints"""
        try:
            # Sort recommendations by ROI (highest first)
            sorted_recs = sorted(
                recommendations,
                key=lambda x: x.get('roi_percentage', 0),
                reverse=True
            )
            
            selected_recommendations = []
            remaining_budget = budget
            total_cost = 0
            total_savings = 0
            
            for rec in sorted_recs:
                cost = rec.get('annual_cost', 0)
                if cost <= remaining_budget:
                    selected_recommendations.append(rec)
                    remaining_budget -= cost
                    total_cost += cost
                    total_savings += rec.get('potential_savings', 0)
            
            return {
                'budget': budget,
                'selected_recommendations': selected_recommendations,
                'total_cost': round(total_cost, 2),
                'total_potential_savings': round(total_savings, 2),
                'remaining_budget': round(remaining_budget, 2),
                'roi_percentage': round((total_savings - total_cost) / total_cost * 100, 1) if total_cost > 0 else 0,
                'currency': 'USD'
            }
            
        except Exception as e:
            logger.error(f"Error optimizing security budget: {str(e)}")
            return {'error': str(e)}

# Initialize MCP server
server = Server("cost-analysis-mcp")
cost_analyzer = CostAnalysisMCP()

@server.list_tools()
async def handle_list_tools() -> List[Tool]:
    """List available cost analysis tools"""
    return [
        Tool(
            name="get_security_costs",
            description="Get current security service costs for an AWS account",
            inputSchema={
                "type": "object",
                "properties": {
                    "account_id": {"type": "string", "description": "AWS account ID"},
                    "days": {"type": "integer", "description": "Number of days to analyze (default: 30)"}
                },
                "required": ["account_id"]
            }
        ),
        Tool(
            name="estimate_recommendation_cost",
            description="Estimate cost impact of security recommendations",
            inputSchema={
                "type": "object",
                "properties": {
                    "recommendation": {
                        "type": "object",
                        "description": "Security recommendation details",
                        "properties": {
                            "service": {"type": "string"},
                            "action": {"type": "string"},
                            "accounts": {"type": "array", "items": {"type": "string"}},
                            "risk_reduction": {"type": "number"}
                        }
                    }
                },
                "required": ["recommendation"]
            }
        ),
        Tool(
            name="calculate_security_roi",
            description="Calculate ROI for security investments",
            inputSchema={
                "type": "object",
                "properties": {
                    "investments": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "annual_cost": {"type": "number"},
                                "potential_savings": {"type": "number"}
                            }
                        }
                    }
                },
                "required": ["investments"]
            }
        ),
        Tool(
            name="get_cost_trends",
            description="Get historical security spending trends",
            inputSchema={
                "type": "object",
                "properties": {
                    "account_ids": {"type": "array", "items": {"type": "string"}},
                    "months": {"type": "integer", "description": "Number of months to analyze (default: 12)"}
                },
                "required": ["account_ids"]
            }
        ),
        Tool(
            name="optimize_security_budget",
            description="Optimize security recommendations within budget constraints",
            inputSchema={
                "type": "object",
                "properties": {
                    "budget": {"type": "number", "description": "Annual budget in USD"},
                    "recommendations": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "annual_cost": {"type": "number"},
                                "potential_savings": {"type": "number"},
                                "roi_percentage": {"type": "number"}
                            }
                        }
                    }
                },
                "required": ["budget", "recommendations"]
            }
        )
    ]

@server.call_tool()
async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle tool calls"""
    try:
        if name == "get_security_costs":
            result = await cost_analyzer.get_security_costs(
                arguments["account_id"],
                arguments.get("days", 30)
            )
        elif name == "estimate_recommendation_cost":
            result = await cost_analyzer.estimate_recommendation_cost(
                arguments["recommendation"]
            )
        elif name == "calculate_security_roi":
            result = await cost_analyzer.calculate_security_roi(
                arguments["investments"]
            )
        elif name == "get_cost_trends":
            result = await cost_analyzer.get_cost_trends(
                arguments["account_ids"],
                arguments.get("months", 12)
            )
        elif name == "optimize_security_budget":
            result = await cost_analyzer.optimize_security_budget(
                arguments["budget"],
                arguments["recommendations"]
            )
        else:
            raise ValueError(f"Unknown tool: {name}")
        
        return [TextContent(type="text", text=json.dumps(result, indent=2))]
        
    except Exception as e:
        logger.error(f"Error in tool {name}: {str(e)}")
        return [TextContent(type="text", text=json.dumps({"error": str(e)}, indent=2))]

async def main():
    """Run the MCP server"""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="cost-analysis-mcp",
                server_version="1.0.0",
                capabilities=server.get_capabilities(
                    notification_options=None,
                    experimental_capabilities=None,
                )
            )
        )

if __name__ == "__main__":
    asyncio.run(main())
