"""
AWS Lambda Handler for Chatbot API
Serverless deployment of the chatbot using AWS Lambda + API Gateway
"""

import json
import os
from chatbot_aws import AWSChatbot

# Initialize chatbot outside handler for Lambda warm starts
chatbot_instances = {}

def lambda_handler(event, context):
    """
    AWS Lambda handler function
    
    Expected event structure:
    {
        "body": {
            "message": "user message here",
            "session_id": "optional-session-id",
            "model_id": "optional-model-id"
        }
    }
    """
    
    try:
        # Parse request body
        if isinstance(event.get('body'), str):
            body = json.loads(event['body'])
        else:
            body = event.get('body', {})
        
        message = body.get('message')
        session_id = body.get('session_id')
        model_id = body.get('model_id')
        
        if not message:
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    'error': 'Message is required',
                    'usage': {
                        'message': 'Your message here',
                        'session_id': 'optional-session-id',
                        'model_id': 'optional-model-id'
                    }
                })
            }
        
        # Get or create chatbot instance for this session
        if session_id and session_id in chatbot_instances:
            chatbot = chatbot_instances[session_id]
        else:
            chatbot = AWSChatbot(model_id=model_id) if model_id else AWSChatbot()
            if session_id:
                chatbot.session_id = session_id
                chatbot_instances[session_id] = chatbot
        
        # Get response
        response_text = chatbot.chat_response(message)
        
        # Return response
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'response': response_text,
                'session_id': chatbot.session_id,
                'model': chatbot.model_id,
                'region': chatbot.aws_region
            })
        }
        
    except Exception as e:
        print(f"Error in lambda_handler: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'error': str(e)
            })
        }


def health_check_handler(event, context):
    """Health check endpoint"""
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json'
        },
        'body': json.dumps({
            'status': 'healthy',
            'service': 'aws-chatbot',
            'version': '1.0.0'
        })
    }

