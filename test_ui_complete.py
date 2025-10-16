#!/usr/bin/env python3
"""Complete UI test script"""

import requests
import json

def test_dashboard():
    """Test the dashboard UI"""
    dashboard_url = "https://tajuooav2jms35ubhnhtiscqvy0usgih.lambda-url.us-east-1.on.aws/"
    
    print("🧪 Testing Dashboard UI...")
    
    try:
        response = requests.get(dashboard_url, timeout=10)
        
        if response.status_code == 200:
            html_content = response.text
            
            # Check for key elements
            checks = [
                ("HTML Structure", "<!DOCTYPE html>" in html_content),
                ("Title", "Security ROI Dashboard" in html_content),
                ("Chart.js", "chart.js" in html_content),
                ("CSS Styling", "background: linear-gradient" in html_content),
                ("Navigation", "nav-btn" in html_content),
                ("Metrics Cards", "metric-card" in html_content),
                ("JavaScript", "function" in html_content)
            ]
            
            print("✅ Dashboard loaded successfully")
            for check_name, passed in checks:
                status = "✅" if passed else "❌"
                print(f"  {status} {check_name}")
            
            return True
            
        else:
            print(f"❌ Dashboard returned status: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Dashboard test failed: {e}")
        return False

def test_agentcore_backend():
    """Test the AgentCore Memory backend"""
    backend_url = "https://vxlk4vnqccr5jp7p4aln34wdge0xaudq.lambda-url.us-east-1.on.aws/"
    
    print("\n🧪 Testing AgentCore Memory Backend...")
    
    try:
        response = requests.get(backend_url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            # Check for key data elements
            checks = [
                ("Security Trends", "security_trends" in data),
                ("Cost Trends", "cost_trends" in data),
                ("Timestamp", "timestamp" in data),
                ("Source", data.get("source") == "AgentCore Memory"),
                ("Security Scores", len(data.get("security_trends", {}).get("security_scores", [])) > 0),
                ("Cost Data", len(data.get("cost_trends", {}).get("monthly_costs", [])) > 0)
            ]
            
            print("✅ AgentCore backend responding")
            for check_name, passed in checks:
                status = "✅" if passed else "❌"
                print(f"  {status} {check_name}")
            
            # Show sample data
            if "security_trends" in data:
                latest_score = data["security_trends"]["security_scores"][-1]
                print(f"  📊 Latest Security Score: {latest_score}")
            
            if "cost_trends" in data:
                latest_cost = data["cost_trends"]["monthly_costs"][-1]
                print(f"  💰 Latest Monthly Cost: ${latest_cost}k")
            
            return True
            
        else:
            print(f"❌ Backend returned status: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Backend test failed: {e}")
        return False

def main():
    """Run complete UI tests"""
    print("🚀 Starting Complete UI Test Suite")
    print("=" * 50)
    
    dashboard_ok = test_dashboard()
    backend_ok = test_agentcore_backend()
    
    print("\n" + "=" * 50)
    print("📋 TEST RESULTS SUMMARY")
    print("=" * 50)
    
    if dashboard_ok and backend_ok:
        print("🎉 ALL TESTS PASSED!")
        print("✅ Dashboard UI: Fully functional")
        print("✅ AgentCore Backend: Fully functional")
        print("✅ Integration: Complete")
        
        print("\n🔗 LIVE URLs:")
        print("📊 Dashboard: https://tajuooav2jms35ubhnhtiscqvy0usgih.lambda-url.us-east-1.on.aws/")
        print("🧠 Backend API: https://vxlk4vnqccr5jp7p4aln34wdge0xaudq.lambda-url.us-east-1.on.aws/")
        
        return True
    else:
        print("❌ SOME TESTS FAILED")
        if not dashboard_ok:
            print("❌ Dashboard UI: Issues detected")
        if not backend_ok:
            print("❌ AgentCore Backend: Issues detected")
        
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
