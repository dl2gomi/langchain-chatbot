"""
Test client for the Chatbot REST API
Demonstrates how to use the API endpoints
"""

import requests
import json
from typing import Optional

class ChatbotAPIClient:
    """Client for interacting with the Chatbot API"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session_id: Optional[str] = None
    
    def health_check(self):
        """Check if the API is healthy"""
        response = requests.get(f"{self.base_url}/health")
        return response.json()
    
    def send_message(self, message: str, session_id: Optional[str] = None, model_id: Optional[str] = None):
        """Send a message to the chatbot"""
        payload = {"message": message}
        
        if session_id or self.session_id:
            payload["session_id"] = session_id or self.session_id
        
        if model_id:
            payload["model_id"] = model_id
        
        response = requests.post(
            f"{self.base_url}/chat",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            # Store session ID for future requests
            self.session_id = data.get("session_id")
            return data
        else:
            return {"error": response.text, "status_code": response.status_code}
    
    def get_history(self, session_id: Optional[str] = None):
        """Get conversation history"""
        sid = session_id or self.session_id
        if not sid:
            return {"error": "No session ID provided"}
        
        response = requests.get(f"{self.base_url}/history/{sid}")
        return response.json()
    
    def get_session_info(self, session_id: Optional[str] = None):
        """Get session information"""
        sid = session_id or self.session_id
        if not sid:
            return {"error": "No session ID provided"}
        
        response = requests.get(f"{self.base_url}/session/{sid}")
        return response.json()
    
    def list_sessions(self):
        """List all active sessions"""
        response = requests.get(f"{self.base_url}/sessions")
        return response.json()
    
    def delete_session(self, session_id: Optional[str] = None):
        """Delete a session"""
        sid = session_id or self.session_id
        if not sid:
            return {"error": "No session ID provided"}
        
        response = requests.delete(f"{self.base_url}/session/{sid}")
        return response.json()
    
    def list_models(self):
        """List available models"""
        response = requests.post(f"{self.base_url}/models/list")
        return response.json()


def demo_conversation():
    """Demo: Have a conversation with the chatbot"""
    print("=" * 60)
    print("Demo: Conversation with Chatbot API")
    print("=" * 60)
    
    client = ChatbotAPIClient()
    
    # Check health
    print("\n1. Health Check")
    health = client.health_check()
    print(f"   Status: {health.get('status')}")
    print(f"   Region: {health.get('aws_region')}")
    
    # Send first message
    print("\n2. Sending First Message")
    response1 = client.send_message("Hello! What is AWS Bedrock?")
    print(f"   Session ID: {response1.get('session_id')}")
    print(f"   Response: {response1.get('response')[:100]}...")
    
    # Send follow-up message (same session)
    print("\n3. Sending Follow-up Message")
    response2 = client.send_message("Can you explain that in simpler terms?")
    print(f"   Session ID: {response2.get('session_id')}")
    print(f"   Response: {response2.get('response')[:100]}...")
    
    # Get session info
    print("\n4. Getting Session Info")
    session_info = client.get_session_info()
    print(f"   User messages: {session_info.get('user_messages')}")
    print(f"   AI messages: {session_info.get('ai_messages')}")
    print(f"   Model: {session_info.get('model')}")
    
    # Get history
    print("\n5. Getting Conversation History")
    history = client.get_history()
    print(f"   Total messages: {len(history)}")
    
    print("\n" + "=" * 60)
    print("Demo Complete!")
    print("=" * 60)


def demo_multiple_sessions():
    """Demo: Multiple concurrent sessions"""
    print("=" * 60)
    print("Demo: Multiple Sessions")
    print("=" * 60)
    
    # Create two separate clients
    client1 = ChatbotAPIClient()
    client2 = ChatbotAPIClient()
    
    # Session 1
    print("\n📝 Session 1:")
    r1 = client1.send_message("Tell me about AWS Lambda")
    print(f"   Session ID: {r1.get('session_id')}")
    print(f"   Response: {r1.get('response')[:80]}...")
    
    # Session 2
    print("\n📝 Session 2:")
    r2 = client2.send_message("Tell me about AWS DynamoDB")
    print(f"   Session ID: {r2.get('session_id')}")
    print(f"   Response: {r2.get('response')[:80]}...")
    
    # List all sessions
    print("\n📋 Active Sessions:")
    sessions = client1.list_sessions()
    for i, sid in enumerate(sessions, 1):
        print(f"   {i}. {sid}")
    
    print("\n" + "=" * 60)


def demo_models():
    """Demo: List and use different models"""
    print("=" * 60)
    print("Demo: Available Models")
    print("=" * 60)
    
    client = ChatbotAPIClient()
    
    # List models
    print("\n📚 Available Models:")
    models_data = client.list_models()
    
    print(f"\n   Total models available: {models_data.get('count', 0)}")
    print(f"   Current default: {models_data.get('current_default', 'N/A')}")
    
    print("\n   Models:")
    for model in models_data.get('models', []):
        print(f"\n   🤖 {model.get('name', 'Unknown')}")
        print(f"      ID: {model.get('id', 'N/A')}")
        print(f"      Provider: {model.get('provider', 'N/A')}")
        if 'input_modalities' in model:
            print(f"      Input: {', '.join(model.get('input_modalities', []))}")
        if 'output_modalities' in model:
            print(f"      Output: {', '.join(model.get('output_modalities', []))}")
    
    print("\n" + "=" * 60)


def interactive_mode():
    """Interactive chat mode"""
    print("=" * 60)
    print("Interactive Chat Mode")
    print("=" * 60)
    print("Commands:")
    print("  'quit' - Exit")
    print("  'history' - Show conversation history")
    print("  'info' - Show session info")
    print("  'new' - Start new session")
    print("=" * 60)
    
    client = ChatbotAPIClient()
    
    while True:
        user_input = input("\nYou: ").strip()
        
        if not user_input:
            continue
        
        if user_input.lower() == 'quit':
            print("Goodbye!")
            break
        
        if user_input.lower() == 'history':
            history = client.get_history()
            print(f"\n📜 Conversation History ({len(history)} messages):")
            for item in history:
                print(f"  [{item['timestamp']}] {item['role']}: {item['content'][:60]}...")
            continue
        
        if user_input.lower() == 'info':
            info = client.get_session_info()
            print(f"\n📊 Session Info:")
            print(f"  Session ID: {info.get('session_id')}")
            print(f"  Model: {info.get('model')}")
            print(f"  Region: {info.get('region')}")
            print(f"  Messages: {info.get('user_messages')} user, {info.get('ai_messages')} AI")
            continue
        
        if user_input.lower() == 'new':
            client.session_id = None
            print("✨ Started new session")
            continue
        
        # Send message
        response = client.send_message(user_input)
        
        if "error" in response:
            print(f"\n❌ Error: {response['error']}")
        else:
            print(f"\n🤖 Assistant: {response['response']}")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "demo":
            demo_conversation()
        elif command == "sessions":
            demo_multiple_sessions()
        elif command == "models":
            demo_models()
        elif command == "interactive":
            interactive_mode()
        else:
            print(f"Unknown command: {command}")
            print("Available commands: demo, sessions, models, interactive")
    else:
        print("AWS Bedrock Chatbot API Client")
        print("\nUsage:")
        print("  python test_api_client.py demo        - Run conversation demo")
        print("  python test_api_client.py sessions    - Demo multiple sessions")
        print("  python test_api_client.py models      - List available models")
        print("  python test_api_client.py interactive - Interactive chat mode")
        print("\nMake sure the API server is running:")
        print("  python api.py")

