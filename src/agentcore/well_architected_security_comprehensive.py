#!/usr/bin/env python3
"""
Comprehensive Well-Architected Security AgentCore Runtime
Adapted from MCP Server with all security services and tools
"""
from bedrock_agentcore.runtime import BedrockAgentCoreApp
import json
import boto3
from datetime import datetime
from typing import Dict, List, Optional

app = BedrockAgentCoreApp()

# Security services configuration
SECURITY_SERVICES = ["guardduty", "inspector", "accessanalyzer", "securityhub", "trustedadvisor", "macie"]
STORAGE_SERVICES = ["s3", "ebs", "rds", "dynamodb", "efs", "elasticache"]
NETWORK_SERVICES = ["elb", "vpc", "apigateway", "cloudfront"]

def check_security_services(region: str = "us-east-1", services: List[str] = None) -> Dict:
    """Check if AWS security services are enabled"""
    if not services:
        services = SECURITY_SERVICES
    
    results = {"region": region, "services": {}, "summary": {"enabled": 0, "total": len(services)}}
    
    for service in services:
        try:
            if service == "guardduty":
                client = boto3.client('guardduty', region_name=region)
                detectors = client.list_detectors()
                enabled = len(detectors.get('DetectorIds', [])) > 0
                
            elif service == "securityhub":
                client = boto3.client('securityhub', region_name=region)
                try:
                    client.describe_hub()
                    enabled = True
                except:
                    enabled = False
                    
            elif service == "inspector":
                client = boto3.client('inspector2', region_name=region)
                try:
                    sts = boto3.client('sts')
                    account_id = sts.get_caller_identity()['Account']
                    status = client.batch_get_account_status(accountIds=[account_id])
                    enabled = status['accounts'][0]['state']['status'] == 'ENABLED'
                except:
                    enabled = False
                    
            elif service == "accessanalyzer":
                client = boto3.client('accessanalyzer', region_name=region)
                analyzers = client.list_analyzers()
                enabled = len(analyzers.get('analyzers', [])) > 0
                
            elif service == "macie":
                client = boto3.client('macie2', region_name=region)
                try:
                    client.get_macie_session()
                    enabled = True
                except:
                    enabled = False
                    
            elif service == "trustedadvisor":
                client = boto3.client('support', region_name='us-east-1')  # Support is global
                try:
                    client.describe_trusted_advisor_checks(language='en')
                    enabled = True
                except:
                    enabled = False
            else:
                enabled = False
                
            results["services"][service] = {"enabled": enabled, "status": "enabled" if enabled else "disabled"}
            if enabled:
                results["summary"]["enabled"] += 1
                
        except Exception as e:
            results["services"][service] = {"enabled": False, "status": "error", "error": str(e)}
    
    return results

def get_security_findings(region: str = "us-east-1", services: List[str] = None, max_findings: int = 100) -> Dict:
    """Get security findings from multiple AWS security services"""
    if not services:
        services = SECURITY_SERVICES
    
    all_findings = {"region": region, "services": {}, "summary": {"total_findings": 0}}
    
    for service in services:
        try:
            findings = []
            
            if service == "securityhub":
                client = boto3.client('securityhub', region_name=region)
                response = client.get_findings(
                    Filters={'RecordState': [{'Value': 'ACTIVE', 'Comparison': 'EQUALS'}]},
                    MaxResults=min(max_findings, 100)
                )
                findings = response.get('Findings', [])
                
            elif service == "guardduty":
                client = boto3.client('guardduty', region_name=region)
                detectors = client.list_detectors()
                for detector_id in detectors.get('DetectorIds', []):
                    response = client.list_findings(DetectorId=detector_id, MaxResults=min(max_findings, 50))
                    finding_ids = response.get('FindingIds', [])
                    if finding_ids:
                        details = client.get_findings(DetectorId=detector_id, FindingIds=finding_ids[:10])
                        findings.extend(details.get('Findings', []))
                        
            elif service == "inspector":
                client = boto3.client('inspector2', region_name=region)
                response = client.list_findings(maxResults=min(max_findings, 100))
                findings = response.get('findings', [])
                
            elif service == "accessanalyzer":
                client = boto3.client('accessanalyzer', region_name=region)
                analyzers = client.list_analyzers()
                for analyzer in analyzers.get('analyzers', []):
                    response = client.list_findings(analyzerArn=analyzer['arn'], maxResults=min(max_findings, 100))
                    findings.extend(response.get('findings', []))
                    
            elif service == "macie":
                client = boto3.client('macie2', region_name=region)
                try:
                    response = client.list_findings(maxResults=min(max_findings, 100))
                    findings = response.get('findingIds', [])
                except:
                    findings = []
                    
            service_count = len(findings)
            all_findings["services"][service] = {
                "findings_count": service_count,
                "sample_findings": findings[:3] if findings else []
            }
            all_findings["summary"]["total_findings"] += service_count
            
        except Exception as e:
            all_findings["services"][service] = {"error": str(e), "findings_count": 0}
    
    return all_findings

def check_storage_encryption(region: str = "us-east-1", services: List[str] = None) -> Dict:
    """Check storage encryption across AWS services"""
    if not services:
        services = STORAGE_SERVICES
    
    results = {"region": region, "services": {}, "summary": {"encrypted": 0, "unencrypted": 0}}
    
    for service in services:
        try:
            if service == "s3":
                client = boto3.client('s3', region_name=region)
                buckets = client.list_buckets()
                encrypted_count = 0
                total_count = len(buckets.get('Buckets', []))
                
                for bucket in buckets.get('Buckets', [])[:10]:  # Check first 10 buckets
                    try:
                        encryption = client.get_bucket_encryption(Bucket=bucket['Name'])
                        if encryption.get('ServerSideEncryptionConfiguration'):
                            encrypted_count += 1
                    except:
                        pass  # No encryption
                        
                results["services"][service] = {
                    "total_resources": total_count,
                    "encrypted": encrypted_count,
                    "unencrypted": total_count - encrypted_count
                }
                
            elif service == "ebs":
                client = boto3.client('ec2', region_name=region)
                volumes = client.describe_volumes()
                encrypted_count = sum(1 for vol in volumes.get('Volumes', []) if vol.get('Encrypted', False))
                total_count = len(volumes.get('Volumes', []))
                
                results["services"][service] = {
                    "total_resources": total_count,
                    "encrypted": encrypted_count,
                    "unencrypted": total_count - encrypted_count
                }
                
            elif service == "rds":
                client = boto3.client('rds', region_name=region)
                instances = client.describe_db_instances()
                encrypted_count = sum(1 for db in instances.get('DBInstances', []) if db.get('StorageEncrypted', False))
                total_count = len(instances.get('DBInstances', []))
                
                results["services"][service] = {
                    "total_resources": total_count,
                    "encrypted": encrypted_count,
                    "unencrypted": total_count - encrypted_count
                }
            else:
                results["services"][service] = {"status": "not_implemented"}
                
            if service in results["services"] and "encrypted" in results["services"][service]:
                results["summary"]["encrypted"] += results["services"][service]["encrypted"]
                results["summary"]["unencrypted"] += results["services"][service]["unencrypted"]
                
        except Exception as e:
            results["services"][service] = {"error": str(e)}
    
    return results

def check_network_security(region: str = "us-east-1", services: List[str] = None) -> Dict:
    """Check network security configurations"""
    if not services:
        services = NETWORK_SERVICES
    
    results = {"region": region, "services": {}, "summary": {"compliant": 0, "non_compliant": 0}}
    
    for service in services:
        try:
            if service == "vpc":
                client = boto3.client('ec2', region_name=region)
                vpcs = client.describe_vpcs()
                security_groups = client.describe_security_groups()
                
                # Check for overly permissive security groups
                risky_sgs = []
                for sg in security_groups.get('SecurityGroups', []):
                    for rule in sg.get('IpPermissions', []):
                        for ip_range in rule.get('IpRanges', []):
                            if ip_range.get('CidrIp') == '0.0.0.0/0':
                                risky_sgs.append(sg['GroupId'])
                                break
                
                results["services"][service] = {
                    "total_vpcs": len(vpcs.get('Vpcs', [])),
                    "total_security_groups": len(security_groups.get('SecurityGroups', [])),
                    "risky_security_groups": len(set(risky_sgs)),
                    "compliant": len(security_groups.get('SecurityGroups', [])) - len(set(risky_sgs))
                }
                
            elif service == "elb":
                client = boto3.client('elbv2', region_name=region)
                load_balancers = client.describe_load_balancers()
                
                https_count = 0
                total_count = len(load_balancers.get('LoadBalancers', []))
                
                for lb in load_balancers.get('LoadBalancers', []):
                    listeners = client.describe_listeners(LoadBalancerArn=lb['LoadBalancerArn'])
                    for listener in listeners.get('Listeners', []):
                        if listener.get('Protocol') in ['HTTPS', 'TLS']:
                            https_count += 1
                            break
                
                results["services"][service] = {
                    "total_load_balancers": total_count,
                    "https_enabled": https_count,
                    "compliant": https_count
                }
            else:
                results["services"][service] = {"status": "not_implemented"}
                
            if service in results["services"] and "compliant" in results["services"][service]:
                results["summary"]["compliant"] += results["services"][service]["compliant"]
                
        except Exception as e:
            results["services"][service] = {"error": str(e)}
    
    return results

@app.entrypoint
async def handler(event):
    """AgentCore entrypoint for comprehensive security analysis"""
    try:
        prompt = event.get("prompt", "").lower()
        
        if "check_security_services" in prompt:
            result = check_security_services()
        elif "get_security_findings" in prompt:
            result = get_security_findings()
        elif "check_storage_encryption" in prompt:
            result = check_storage_encryption()
        elif "check_network_security" in prompt:
            result = check_network_security()
        elif "comprehensive_analysis" in prompt:
            result = {
                "security_services": check_security_services(),
                "security_findings": get_security_findings(),
                "storage_encryption": check_storage_encryption(),
                "network_security": check_network_security(),
                "analysis_timestamp": datetime.now().isoformat()
            }
        else:
            result = {
                "available_tools": [
                    "check_security_services - Check if AWS security services are enabled",
                    "get_security_findings - Get findings from multiple security services",
                    "check_storage_encryption - Check storage encryption status",
                    "check_network_security - Check network security configurations",
                    "comprehensive_analysis - Run all security checks"
                ],
                "supported_services": {
                    "security": SECURITY_SERVICES,
                    "storage": STORAGE_SERVICES,
                    "network": NETWORK_SERVICES
                }
            }
        
        return {"body": json.dumps(result, indent=2, default=str)}
        
    except Exception as e:
        return {"body": json.dumps({"error": str(e)}, indent=2)}

if __name__ == "__main__":
    app.run()
