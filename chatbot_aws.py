"""
AWS-Powered LangChain Chatbot
Uses AWS Bedrock for LLM and DynamoDB for conversation history storage
"""

import os
import json
import uuid
from datetime import datetime
from dotenv import load_dotenv
import boto3
from botocore.exceptions import ClientError
from langchain_aws import ChatBedrock
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage

# Load environment variables
load_dotenv()

class AWSChatbot:
    """AWS Bedrock-powered chatbot with DynamoDB conversation storage"""
    
    def __init__(self, 
                 aws_region=None,
                 model_id=None,
                 dynamodb_table=None):
        """
        Initialize AWS Chatbot
        
        Args:
            aws_region: AWS region (defaults to env var AWS_REGION or us-east-1)
            model_id: Bedrock model ID (defaults to env var BEDROCK_MODEL_ID or amazon.nova-pro-v1:0)
            dynamodb_table: DynamoDB table name (defaults to env var DYNAMODB_TABLE_NAME or ChatbotConversations)
        """
        self.aws_region = aws_region or os.getenv("AWS_REGION", "us-east-1")
        self.model_id = model_id or os.getenv("BEDROCK_MODEL_ID", "us.amazon.nova-pro-v1:0")
        self.dynamodb_table = dynamodb_table or os.getenv("DYNAMODB_TABLE_NAME", "ChatbotConversations")
        self.session_id = str(uuid.uuid4())
        
        # Initialize AWS clients
        self.bedrock_client = boto3.client(
            service_name='bedrock-runtime',
            region_name=self.aws_region
        )
        
        self.dynamodb = boto3.resource('dynamodb', region_name=self.aws_region)
        
        # Initialize LangChain ChatBedrock
        self.chat = ChatBedrock(
            client=self.bedrock_client,
            model_id=self.model_id,
            model_kwargs={
                "temperature": 0.7,
                "max_tokens": 2048,
            }
        )
        
        # Conversation history
        self.messages = [
            SystemMessage(content="You are a helpful AI assistant powered by AWS. Be concise and friendly.")
        ]
        
        print(f"✓ Connected to AWS Bedrock ({self.aws_region})")
        print(f"✓ Using model: {self.model_id}")
        print(f"✓ Session ID: {self.session_id}")
    
    def save_message_to_dynamodb(self, role, content):
        """Save a message to DynamoDB"""
        try:
            table = self.dynamodb.Table(self.dynamodb_table)
            
            item = {
                'SessionId': self.session_id,
                'Timestamp': datetime.utcnow().isoformat(),
                'MessageId': str(uuid.uuid4()),
                'Role': role,
                'Content': content
            }
            
            table.put_item(Item=item)
        except ClientError as e:
            print(f"Warning: Could not save to DynamoDB: {e.response['Error']['Message']}")
            print("Conversation will continue without persistence.")
        except Exception as e:
            print(f"Warning: DynamoDB error: {str(e)}")
    
    def get_conversation_history(self, session_id=None):
        """Retrieve conversation history from DynamoDB"""
        try:
            table = self.dynamodb.Table(self.dynamodb_table)
            session_id = session_id or self.session_id
            
            response = table.query(
                KeyConditionExpression='SessionId = :sid',
                ExpressionAttributeValues={':sid': session_id}
            )
            
            return response.get('Items', [])
        except Exception as e:
            print(f"Could not retrieve history: {str(e)}")
            return []
    
    def chat_response(self, user_input):
        """
        Get a response from the chatbot
        
        Args:
            user_input: User's message
            
        Returns:
            str: Chatbot's response
        """
        # Add user message
        self.messages.append(HumanMessage(content=user_input))
        self.save_message_to_dynamodb("user", user_input)
        
        # Get AI response
        try:
            response = self.chat.invoke(self.messages)
            assistant_message = response.content
            
            # Add to conversation history
            self.messages.append(AIMessage(content=assistant_message))
            self.save_message_to_dynamodb("assistant", assistant_message)
            
            return assistant_message
        except Exception as e:
            error_msg = f"Error getting response: {str(e)}"
            print(error_msg)
            return error_msg
    
    def get_session_summary(self):
        """Get summary of current session"""
        user_messages = sum(1 for m in self.messages if isinstance(m, HumanMessage))
        ai_messages = sum(1 for m in self.messages if isinstance(m, AIMessage))
        
        return {
            "session_id": self.session_id,
            "region": self.aws_region,
            "model": self.model_id,
            "user_messages": user_messages,
            "ai_messages": ai_messages
        }


def interactive_chat():
    """Run an interactive chat session"""
    print("=" * 60)
    print("AWS Bedrock Chatbot with DynamoDB Storage")
    print("=" * 60)
    print("Type 'quit', 'exit', or 'bye' to end the conversation.")
    print("Type 'history' to see conversation history.")
    print("Type 'summary' to see session summary.")
    print("-" * 60)
    
    # Initialize chatbot
    try:
        chatbot = AWSChatbot()
    except Exception as e:
        print(f"\n❌ Error initializing chatbot: {e}")
        print("\nPlease check:")
        print("1. AWS credentials are configured (aws configure)")
        print("2. You have access to AWS Bedrock")
        print("3. DynamoDB table exists (run setup_dynamodb.py)")
        return
    
    print("\n✓ Chatbot ready! Start chatting...\n")
    
    while True:
        # Get user input
        user_input = input("\nYou: ").strip()
        
        # Handle special commands
        if user_input.lower() in ['quit', 'exit', 'bye']:
            summary = chatbot.get_session_summary()
            print(f"\n👋 Goodbye!")
            print(f"Session Summary: {summary['user_messages']} messages exchanged")
            print(f"Session ID: {summary['session_id']}")
            break
        
        if user_input.lower() == 'history':
            history = chatbot.get_conversation_history()
            print(f"\n📜 Conversation History ({len(history)} messages):")
            for item in history:
                print(f"  [{item['Timestamp']}] {item['Role']}: {item['Content'][:50]}...")
            continue
        
        if user_input.lower() == 'summary':
            summary = chatbot.get_session_summary()
            print(f"\n📊 Session Summary:")
            for key, value in summary.items():
                print(f"  {key}: {value}")
            continue
        
        if not user_input:
            print("Please enter a message.")
            continue
        
        # Get response
        response = chatbot.chat_response(user_input)
        print(f"\n🤖 Assistant: {response}")


def simple_query(question, model_id=None):
    """
    Simple one-off query
    
    Args:
        question: The question to ask
        model_id: Optional specific model ID
        
    Returns:
        str: The response
    """
    try:
        chatbot = AWSChatbot(model_id=model_id) if model_id else AWSChatbot()
        return chatbot.chat_response(question)
    except Exception as e:
        return f"Error: {str(e)}"


if __name__ == "__main__":
    # Run interactive chat
    interactive_chat()
    
    # Example of simple query:
    # answer = simple_query("What are the benefits of using AWS?")
    # print(answer)

