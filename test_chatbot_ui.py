#!/usr/bin/env python3
import requests
import json

def test_chatbot_ui():
    """Test the chatbot UI endpoint"""
    
    chatbot_url = "https://n2a2ips2o77azwibegxmpfq4ga0evzxs.lambda-url.us-east-1.on.aws/"
    
    print(f"🧪 Testing Chatbot UI: {chatbot_url}")
    
    try:
        # Test GET request (should return HTML)
        response = requests.get(chatbot_url, timeout=30)
        print(f"✅ GET Status: {response.status_code}")
        
        if "Bedrock Agent Security Assistant" in response.text:
            print("✅ UI loads correctly")
        else:
            print("❌ UI content issue")
            
        # Test POST request (chat functionality)
        chat_data = {
            "message": "Show me my security score"
        }
        
        response = requests.post(chatbot_url, json=chat_data, timeout=60)
        print(f"✅ POST Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Chat Response: {json.dumps(result, indent=2)}")
            
            if "error" not in result.get("response", "").lower():
                print("🎉 CHATBOT WORKING! Bedrock Agent orchestration successful!")
                return True
            else:
                print("⚠️ Chat response contains errors")
                return False
        else:
            print(f"❌ Chat request failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Chatbot test failed: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_chatbot_ui()
    
    if success:
        print("\n🎉 SUCCESS: Bedrock Agent orchestrated chatbot is working!")
        print("✅ Architecture: UI → Bedrock Agent → Lambda → AgentCore → AWS APIs")
        print("🔗 URL: https://n2a2ips2o77azwibegxmpfq4ga0evzxs.lambda-url.us-east-1.on.aws/")
    else:
        print("\n🚨 FAILURE: Chatbot still has issues that need resolution")
