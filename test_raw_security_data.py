#!/usr/bin/env python3
"""
Get raw unformatted data from analyze_security_posture tool
"""

import sys
import os
import json

# Add project paths
sys.path.append('src')
sys.path.append('src/agentcore')

def get_raw_security_data():
    """Get raw data from analyze_security_posture"""
    
    try:
        from well_architected_security_agentcore import analyze_security_posture
        
        print("🔍 RAW DATA FROM analyze_security_posture:")
        print("="*80)
        
        # Get raw data
        raw_data = analyze_security_posture("123456789012")
        
        # Print raw JSON without formatting
        print(json.dumps(raw_data, separators=(',', ':')))
        
        return raw_data
        
    except Exception as e:
        print(f"Error: {e}")
        return None

if __name__ == "__main__":
    get_raw_security_data()
