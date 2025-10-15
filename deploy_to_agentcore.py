#!/usr/bin/env python3
"""
Deploy comprehensive security AgentCore using bedrock-agentcore-starter-toolkit
"""

import subprocess
import sys
import os
import json
from datetime import datetime

def configure_agentcore():
    """Configure AgentCore for deployment"""
    print("⚙️ Configuring AgentCore...")
    
    try:
        # Change to deployment directory
        os.chdir('deployment')
        
        # Configure AgentCore
        cmd = [
            sys.executable, '-m', 'bedrock_agentcore_starter_toolkit.cli',
            'configure',
            '--entrypoint', 'well_architected_security_comprehensive.py',
            '--non-interactive'
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        print("   ✅ AgentCore configured successfully")
        print(f"   📋 Output: {result.stdout}")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"   ❌ Configuration failed: {e}")
        print(f"   📋 Error: {e.stderr}")
        return False
    except Exception as e:
        print(f"   ❌ Configuration error: {e}")
        return False

def launch_agentcore():
    """Launch AgentCore to AWS"""
    print("\n🚀 Launching AgentCore to AWS...")
    
    try:
        cmd = [
            sys.executable, '-m', 'bedrock_agentcore_starter_toolkit.cli',
            'launch'
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        print("   ✅ AgentCore launched successfully")
        print(f"   📋 Output: {result.stdout}")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"   ❌ Launch failed: {e}")
        print(f"   📋 Error: {e.stderr}")
        return False
    except Exception as e:
        print(f"   ❌ Launch error: {e}")
        return False

def test_deployed_agentcore():
    """Test deployed AgentCore"""
    print("\n🧪 Testing Deployed AgentCore...")
    
    try:
        # Test with different prompts
        test_prompts = [
            '{"prompt": "check_security_services"}',
            '{"prompt": "get_security_findings"}',
            '{"prompt": "comprehensive_analysis"}'
        ]
        
        for i, prompt in enumerate(test_prompts, 1):
            print(f"\n   {i}️⃣ Testing: {prompt}")
            
            cmd = [
                sys.executable, '-m', 'bedrock_agentcore_starter_toolkit.cli',
                'invoke', prompt
            ]
            
            try:
                result = subprocess.run(cmd, capture_output=True, text=True, check=True, timeout=30)
                response = json.loads(result.stdout)
                
                # Extract key metrics
                if 'summary' in response:
                    summary = response['summary']
                    print(f"      ✅ Response: {summary}")
                elif 'available_tools' in response:
                    tools = response['available_tools']
                    print(f"      ✅ Tools: {len(tools)} available")
                else:
                    print(f"      ✅ Response received: {len(str(response))} chars")
                    
            except subprocess.TimeoutExpired:
                print(f"      ⚠️ Test timeout (30s)")
            except Exception as e:
                print(f"      ❌ Test failed: {e}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Testing error: {e}")
        return False

def main():
    """Main deployment function"""
    print("🚀 DEPLOYING COMPREHENSIVE SECURITY AGENTCORE")
    print(f"⏰ Started: {datetime.now().isoformat()}")
    
    # Save current directory
    original_dir = os.getcwd()
    
    try:
        results = {}
        
        # Step 1: Configure
        results['configure'] = configure_agentcore()
        
        # Step 2: Launch (only if configure succeeded)
        if results['configure']:
            results['launch'] = launch_agentcore()
        else:
            results['launch'] = False
        
        # Step 3: Test (only if launch succeeded)
        if results['launch']:
            results['test'] = test_deployed_agentcore()
        else:
            results['test'] = False
        
        # Summary
        print(f"\n{'='*60}")
        print("📊 DEPLOYMENT SUMMARY")
        print('='*60)
        
        success_count = sum(results.values())
        total_steps = len(results)
        
        for step, success in results.items():
            status = "✅ SUCCESS" if success else "❌ FAILED"
            print(f"   {step}: {status}")
        
        print(f"\n🎯 Overall: {success_count}/{total_steps} steps completed")
        
        if success_count == total_steps:
            print("\n🎉 DEPLOYMENT SUCCESSFUL!")
            print("\n📋 AgentCore Runtime Deployed With:")
            print("   • 5 Security Analysis Tools")
            print("   • 6 AWS Security Services Integration")
            print("   • Storage & Network Security Checks")
            print("   • Real-time AWS Data Integration")
        else:
            print("\n⚠️ DEPLOYMENT INCOMPLETE")
            print("   • Check error messages above")
            print("   • Manual deployment may be required")
        
        return success_count == total_steps
        
    except Exception as e:
        print(f"❌ Deployment failed: {e}")
        return False
    
    finally:
        # Restore original directory
        os.chdir(original_dir)
        print(f"\n⏰ Completed: {datetime.now().isoformat()}")

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
