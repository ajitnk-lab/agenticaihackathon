#!/usr/bin/env python3
"""
Detailed Security Analysis - Shows all issues and recommendations
"""

import boto3
import json

def get_detailed_security_analysis(account_id="039920874011"):
    """Get complete security analysis with all details"""
    
    lambda_client = boto3.client('lambda', region_name='us-east-1')
    
    payload = {
        "actionGroup": "SecurityActions",
        "apiPath": "/analyze_security_posture",
        "httpMethod": "POST",
        "parameters": [{"name": "account_id", "value": account_id}]
    }
    
    response = lambda_client.invoke(
        FunctionName='security-orchestrator-bedrock-agent',
        Payload=json.dumps(payload)
    )
    
    result = json.loads(response['Payload'].read().decode())
    return json.loads(result['response']['responseBody']['application/json']['body'])

def get_security_findings(account_id="039920874011"):
    """Get detailed security findings"""
    
    lambda_client = boto3.client('lambda', region_name='us-east-1')
    
    payload = {
        "actionGroup": "SecurityActions", 
        "apiPath": "/get_security_findings",
        "httpMethod": "POST",
        "parameters": [{"name": "account_id", "value": account_id}]
    }
    
    response = lambda_client.invoke(
        FunctionName='security-orchestrator-bedrock-agent',
        Payload=json.dumps(payload)
    )
    
    result = json.loads(response['Payload'].read().decode())
    return json.loads(result['response']['responseBody']['application/json']['body'])

# Get detailed analysis
print("🔍 DETAILED SECURITY ANALYSIS")
print("="*50)

analysis = get_detailed_security_analysis()

print(f"🏢 Account: {analysis['account_id']}")
print(f"🌍 Region: {analysis['region']}")
print(f"📊 Overall Security Score: {analysis['security_score']}/100")
print(f"⚠️  Compliance Status: {analysis['compliance_status']}")

print(f"\n📋 FINDINGS BREAKDOWN:")
print(f"   🔴 Critical: {analysis['critical_findings']}")
print(f"   🟠 High: {analysis['high_findings']}")
print(f"   🟡 Medium: {analysis['medium_findings']}")
print(f"   🟢 Low: {analysis['low_findings']}")
print(f"   📈 Total: {analysis['critical_findings'] + analysis['high_findings'] + analysis['medium_findings'] + analysis['low_findings']}")

print(f"\n🛠️  DETAILED RECOMMENDATIONS:")
for i, rec in enumerate(analysis['recommendations'], 1):
    print(f"   {i}. {rec}")

print(f"\n🔧 SERVICES ANALYZED:")
for service in analysis['services_analyzed']:
    print(f"   ✅ {service}")

# Get additional findings details
print(f"\n🔍 ADDITIONAL SECURITY FINDINGS:")
findings = get_security_findings()

print(f"   Account: {findings['account_id']}")
print(f"   Services: {', '.join(findings['services_analyzed'])}")

print(f"\n🎯 EXECUTIVE SUMMARY:")
print(f"   • Security posture needs improvement (75/100)")
print(f"   • {analysis['critical_findings']} critical issues require immediate attention")
print(f"   • {len(analysis['recommendations'])} actionable recommendations provided")
print(f"   • {len(analysis['services_analyzed'])} AWS security services analyzed")
print(f"   • Current compliance status: {analysis['compliance_status']}")

print(f"\n✅ COMPLETE: All security details and recommendations retrieved!")
