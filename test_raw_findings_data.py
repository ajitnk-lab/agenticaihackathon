#!/usr/bin/env python3
"""
Get raw unformatted data from get_security_findings tool
"""

import sys
import os
import json

# Add project paths
sys.path.append('src')
sys.path.append('src/agentcore')

def get_raw_findings_data():
    """Get raw data from get_security_findings"""
    
    try:
        from well_architected_security_agentcore import get_security_findings
        
        print("🔍 RAW DATA FROM get_security_findings:")
        print("="*80)
        
        # Get raw data
        raw_data = get_security_findings("123456789012")
        
        # Print raw JSON without formatting
        print(json.dumps(raw_data, separators=(',', ':')))
        
        return raw_data
        
    except Exception as e:
        print(f"Error: {e}")
        return None

if __name__ == "__main__":
    get_raw_findings_data()
