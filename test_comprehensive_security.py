#!/usr/bin/env python3
"""
Test comprehensive Well-Architected Security AgentCore runtime
"""

import sys
import os
import json
import asyncio
from datetime import datetime

# Add project paths
sys.path.append('src')
sys.path.append('src/agentcore')

async def test_comprehensive_tools():
    """Test all comprehensive security tools"""
    
    print("🚀 COMPREHENSIVE WELL-ARCHITECTED SECURITY AGENTCORE TEST")
    print(f"⏰ Test Started: {datetime.now().isoformat()}")
    
    try:
        from well_architected_security_comprehensive import handler
        
        # Test all tools
        test_prompts = [
            "check_security_services",
            "get_security_findings", 
            "check_storage_encryption",
            "check_network_security",
            "comprehensive_analysis",
            "show available tools"
        ]
        
        results = {}
        
        for i, prompt in enumerate(test_prompts, 1):
            print(f"\n{'='*60}")
            print(f"🔧 TEST {i}: {prompt}")
            print('='*60)
            
            try:
                event = {"prompt": prompt}
                result = await handler(event)
                response_data = json.loads(result["body"])
                
                # Extract key metrics
                if "security_services" in response_data:
                    services = response_data["security_services"]
                    enabled = services.get("summary", {}).get("enabled", 0)
                    total = services.get("summary", {}).get("total", 0)
                    print(f"   ✅ Security Services: {enabled}/{total} enabled")
                    
                elif "security_findings" in response_data:
                    findings = response_data["security_findings"]
                    total_findings = findings.get("summary", {}).get("total_findings", 0)
                    print(f"   ✅ Security Findings: {total_findings} total findings")
                    
                elif "storage_encryption" in response_data:
                    storage = response_data["storage_encryption"]
                    encrypted = storage.get("summary", {}).get("encrypted", 0)
                    unencrypted = storage.get("summary", {}).get("unencrypted", 0)
                    print(f"   ✅ Storage Encryption: {encrypted} encrypted, {unencrypted} unencrypted")
                    
                elif "network_security" in response_data:
                    network = response_data["network_security"]
                    compliant = network.get("summary", {}).get("compliant", 0)
                    print(f"   ✅ Network Security: {compliant} compliant resources")
                    
                elif "available_tools" in response_data:
                    tools = response_data["available_tools"]
                    print(f"   ✅ Available Tools: {len(tools)}")
                    for tool in tools:
                        print(f"      • {tool}")
                        
                elif "services" in response_data:
                    # Individual tool response
                    if "summary" in response_data:
                        summary = response_data["summary"]
                        print(f"   ✅ Summary: {summary}")
                    
                    services = response_data["services"]
                    print(f"   📊 Services checked: {len(services)}")
                    for service, status in services.items():
                        if isinstance(status, dict):
                            if "enabled" in status:
                                print(f"      • {service}: {'✅' if status['enabled'] else '❌'}")
                            elif "error" in status:
                                print(f"      • {service}: ❌ Error")
                            else:
                                print(f"      • {service}: 📊 Data available")
                
                results[prompt] = True
                
            except Exception as e:
                print(f"   ❌ Error: {e}")
                results[prompt] = False
        
        # Summary
        print(f"\n{'='*60}")
        print("📊 TEST SUMMARY")
        print('='*60)
        
        passed = sum(results.values())
        total = len(results)
        
        for test_name, passed_test in results.items():
            status = "✅ PASSED" if passed_test else "❌ FAILED"
            print(f"   {test_name}: {status}")
        
        print(f"\n🎯 Overall: {passed}/{total} tests passed")
        
        if passed == total:
            print("\n🎉 ALL COMPREHENSIVE SECURITY TOOLS WORKING!")
        else:
            print(f"\n⚠️ {total - passed} test(s) failed")
        
        print(f"\n⏰ Test Completed: {datetime.now().isoformat()}")
        
        return passed == total
        
    except Exception as e:
        print(f"❌ Test setup error: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_comprehensive_tools())
    sys.exit(0 if success else 1)
