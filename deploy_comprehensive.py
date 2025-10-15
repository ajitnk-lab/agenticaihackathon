#!/usr/bin/env python3
"""
Deploy comprehensive Well-Architected Security AgentCore
"""

import subprocess
import sys
import os
from datetime import datetime

def run_command(cmd, description):
    """Run command and handle errors"""
    print(f"🔧 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        print(f"   ✅ Success: {description}")
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"   ❌ Failed: {description}")
        print(f"   Error: {e.stderr}")
        return None

def build_docker_image():
    """Build Docker image for comprehensive security AgentCore"""
    print("🐳 Building Docker Image...")
    
    # Build image
    cmd = "docker build -f Dockerfile.comprehensive -t well-architected-security-comprehensive:latest ."
    result = run_command(cmd, "Building Docker image")
    
    if result is not None:
        # List images
        run_command("docker images | grep well-architected-security-comprehensive", "Listing built image")
        return True
    return False

def test_docker_image():
    """Test Docker image locally"""
    print("\n🧪 Testing Docker Image...")
    
    # Run container in background
    cmd = "docker run -d --name test-comprehensive -p 8001:8000 well-architected-security-comprehensive:latest"
    container_id = run_command(cmd, "Starting test container")
    
    if container_id:
        # Wait for startup
        import time
        time.sleep(5)
        
        # Check container status
        run_command("docker ps | grep test-comprehensive", "Checking container status")
        
        # Check logs
        run_command("docker logs test-comprehensive", "Checking container logs")
        
        # Cleanup
        run_command("docker stop test-comprehensive", "Stopping test container")
        run_command("docker rm test-comprehensive", "Removing test container")
        
        return True
    return False

def deploy_to_agentcore():
    """Deploy to AgentCore platform"""
    print("\n🚀 Deploying to AgentCore...")
    
    # Check if agentcore CLI is available
    result = run_command("which agentcore || echo 'AgentCore CLI not found'", "Checking AgentCore CLI")
    
    if "not found" in str(result):
        print("   ⚠️ AgentCore CLI not available - manual deployment required")
        print("   📋 Manual deployment steps:")
        print("      1. Upload well_architected_security_comprehensive.py to AgentCore")
        print("      2. Upload .bedrock_agentcore_comprehensive.yaml as .bedrock_agentcore.yaml")
        print("      3. Deploy using AgentCore console or CLI")
        return False
    
    # Deploy using AgentCore CLI
    cmd = "agentcore deploy src/agentcore/well_architected_security_comprehensive.py"
    result = run_command(cmd, "Deploying to AgentCore")
    
    return result is not None

def main():
    """Main deployment function"""
    print("🚀 COMPREHENSIVE WELL-ARCHITECTED SECURITY AGENTCORE DEPLOYMENT")
    print(f"⏰ Deployment Started: {datetime.now().isoformat()}")
    
    success_count = 0
    total_steps = 3
    
    # Step 1: Build Docker image
    if build_docker_image():
        success_count += 1
    
    # Step 2: Test Docker image
    if test_docker_image():
        success_count += 1
    
    # Step 3: Deploy to AgentCore
    if deploy_to_agentcore():
        success_count += 1
    
    # Summary
    print(f"\n{'='*60}")
    print("📊 DEPLOYMENT SUMMARY")
    print('='*60)
    
    print(f"🎯 Steps completed: {success_count}/{total_steps}")
    
    if success_count == total_steps:
        print("🎉 DEPLOYMENT SUCCESSFUL!")
        print("\n📋 Next Steps:")
        print("   • Test AgentCore runtime with: python3 test_comprehensive_security.py")
        print("   • Access via Bedrock Agent integration")
        print("   • Monitor logs and performance")
    else:
        print("⚠️ PARTIAL DEPLOYMENT - Some steps failed")
        print("\n📋 Manual Steps Required:")
        print("   • Check error messages above")
        print("   • Complete failed deployment steps manually")
    
    print(f"\n⏰ Deployment Completed: {datetime.now().isoformat()}")
    
    return success_count == total_steps

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
