#!/usr/bin/env python3
"""Deploy Well-Architected Security MCP Server to AgentCore Runtime"""

import boto3
import json
import zipfile
import os
from pathlib import Path

def create_mcp_package():
    """Package MCP server for deployment"""
    package_path = Path("mcp-server-package.zip")
    
    with zipfile.ZipFile(package_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # Add MCP server source files
        mcp_src = Path("mcp-servers/src")
        for file_path in mcp_src.rglob("*.py"):
            zipf.write(file_path, file_path.relative_to(mcp_src.parent))
        
        # Add requirements
        zipf.write("mcp-servers/pyproject.toml", "pyproject.toml")
    
    return package_path

def deploy_to_agentcore():
    """Deploy MCP server to AgentCore Runtime"""
    # Create package
    package_path = create_mcp_package()
    
    # Upload to S3 (will be handled by CDK deployment)
    print(f"✅ MCP server package created: {package_path}")
    print("📦 Package will be deployed via CDK stack")
    
    return str(package_path)

if __name__ == "__main__":
    try:
        package_path = deploy_to_agentcore()
        print(f"🚀 MCP server ready for deployment: {package_path}")
    except Exception as e:
        print(f"❌ Deployment failed: {e}")
