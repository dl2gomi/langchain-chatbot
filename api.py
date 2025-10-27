"""
RESTful API Backend for AWS Chatbot
Built with FastAPI for high performance and automatic API documentation
"""

from fastapi import FastAPI, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List, Dict
import uuid
from datetime import datetime
from chatbot_aws import AWSChatbot
import os

# Initialize FastAPI app
app = FastAPI(
    title="AWS Bedrock Chatbot API",
    description="RESTful API for conversational AI powered by AWS Bedrock and DynamoDB",
    version="1.0.0",
    docs_url="/docs",  # Swagger UI
    redoc_url="/redoc"  # ReDoc
)

# CORS configuration - adjust origins for production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory session storage (for stateful connections)
# In production, use Redis or similar
chatbot_sessions: Dict[str, AWSChatbot] = {}


# Pydantic models for request/response validation
class ChatRequest(BaseModel):
    message: str = Field(..., description="User's message", min_length=1, max_length=5000)
    session_id: Optional[str] = Field(None, description="Session ID for conversation continuity")
    model_id: Optional[str] = Field(None, description="Override default Bedrock model")
    
    class Config:
        json_schema_extra = {
            "example": {
                "message": "What is AWS Lambda?",
                "session_id": "optional-session-id",
                "model_id": "anthropic.claude-3-sonnet-20240229-v1:0"
            }
        }


class ChatResponse(BaseModel):
    response: str = Field(..., description="AI assistant's response")
    session_id: str = Field(..., description="Session ID for this conversation")
    model: str = Field(..., description="Model ID used for this response")
    region: str = Field(..., description="AWS region")
    timestamp: str = Field(..., description="Response timestamp")


class SessionInfo(BaseModel):
    session_id: str
    region: str
    model: str
    user_messages: int
    ai_messages: int
    created_at: str


class HistoryItem(BaseModel):
    timestamp: str
    role: str
    content: str
    message_id: str


class HealthResponse(BaseModel):
    status: str
    service: str
    version: str
    aws_region: str
    timestamp: str


# API Endpoints

@app.get("/", response_model=Dict[str, str])
async def root():
    """Root endpoint - API information"""
    return {
        "service": "AWS Bedrock Chatbot API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
        "endpoints": {
            "chat": "POST /chat",
            "history": "GET /history/{session_id}",
            "session": "GET /session/{session_id}",
            "sessions": "GET /sessions"
        }
    }


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        service="aws-bedrock-chatbot",
        version="1.0.0",
        aws_region=os.getenv("AWS_REGION", "us-east-1"),
        timestamp=datetime.utcnow().isoformat()
    )


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Send a message to the chatbot and get a response
    
    - **message**: Your message to the AI
    - **session_id**: Optional session ID to continue a conversation
    - **model_id**: Optional model override
    """
    try:
        # Get or create chatbot instance
        session_id = request.session_id or str(uuid.uuid4())
        
        if session_id in chatbot_sessions:
            chatbot = chatbot_sessions[session_id]
        else:
            # Create new chatbot instance
            if request.model_id:
                chatbot = AWSChatbot(model_id=request.model_id)
            else:
                chatbot = AWSChatbot()  # Use default model
            
            chatbot.session_id = session_id
            chatbot_sessions[session_id] = chatbot
        
        # Get response
        response_text = chatbot.chat_response(request.message)
        
        return ChatResponse(
            response=response_text,
            session_id=session_id,
            model=chatbot.model_id,
            region=chatbot.aws_region,
            timestamp=datetime.utcnow().isoformat()
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing chat request: {str(e)}"
        )


@app.get("/history/{session_id}", response_model=List[HistoryItem])
async def get_history(session_id: str):
    """
    Get conversation history for a specific session
    
    - **session_id**: The session ID to retrieve history for
    """
    try:
        # Create a temporary chatbot instance to access DynamoDB
        chatbot = AWSChatbot()
        history = chatbot.get_conversation_history(session_id)
        
        return [
            HistoryItem(
                timestamp=item.get('Timestamp', ''),
                role=item.get('Role', ''),
                content=item.get('Content', ''),
                message_id=item.get('MessageId', '')
            )
            for item in history
        ]
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving history: {str(e)}"
        )


@app.get("/session/{session_id}", response_model=SessionInfo)
async def get_session_info(session_id: str):
    """
    Get information about a specific session
    
    - **session_id**: The session ID to get information for
    """
    if session_id not in chatbot_sessions:
        raise HTTPException(
            status_code=404,
            detail=f"Session {session_id} not found in active sessions"
        )
    
    chatbot = chatbot_sessions[session_id]
    summary = chatbot.get_session_summary()
    
    return SessionInfo(
        session_id=summary['session_id'],
        region=summary['region'],
        model=summary['model'],
        user_messages=summary['user_messages'],
        ai_messages=summary['ai_messages'],
        created_at=datetime.utcnow().isoformat()
    )


@app.get("/sessions", response_model=List[str])
async def list_active_sessions():
    """Get list of active session IDs"""
    return list(chatbot_sessions.keys())


@app.delete("/session/{session_id}")
async def delete_session(session_id: str):
    """
    Delete a session from memory (doesn't delete from DynamoDB)
    
    - **session_id**: The session ID to delete
    """
    if session_id in chatbot_sessions:
        del chatbot_sessions[session_id]
        return {"message": f"Session {session_id} deleted", "status": "success"}
    else:
        raise HTTPException(
            status_code=404,
            detail=f"Session {session_id} not found"
        )


@app.post("/models/list")
async def list_available_models():
    """List available Bedrock models from AWS"""
    try:
        import boto3
        from botocore.exceptions import ClientError
        
        bedrock = boto3.client(
            'bedrock',
            region_name=os.getenv("AWS_REGION", "us-east-1")
        )
        
        # Get available models from AWS Bedrock
        response = bedrock.list_foundation_models()
        
        models = []
        for model in response.get('modelSummaries', []):
            # Only include models that support text generation
            if 'TEXT' in model.get('outputModalities', []):
                models.append({
                    "id": model.get('modelId'),
                    "name": model.get('modelName'),
                    "provider": model.get('providerName'),
                    "input_modalities": model.get('inputModalities', []),
                    "output_modalities": model.get('outputModalities', []),
                    "status": "available"
                })
        
        # Sort by provider and name
        models.sort(key=lambda x: (x['provider'], x['name']))
        
        return {
            "models": models,
            "count": len(models),
            "current_default": os.getenv("BEDROCK_MODEL_ID", "us.amazon.nova-pro-v1:0"),
            "note": "Use models with 'TEXT' in output_modalities for chat"
        }
        
    except ClientError as e:
        # Fallback to common models if can't access Bedrock
        return {
            "models": [
                {
                    "id": "us.amazon.nova-pro-v1:0",
                    "name": "Amazon Nova Pro",
                    "provider": "Amazon",
                    "note": "Default model - use region-prefixed ID"
                },
                {
                    "id": "us.amazon.nova-lite-v1:0",
                    "name": "Amazon Nova Lite",
                    "provider": "Amazon"
                },
                {
                    "id": "us.amazon.nova-micro-v1:0",
                    "name": "Amazon Nova Micro",
                    "provider": "Amazon"
                }
            ],
            "count": 3,
            "current_default": os.getenv("BEDROCK_MODEL_ID", "us.amazon.nova-pro-v1:0"),
            "note": "Limited list - enable full access in AWS Bedrock console. Use region-prefixed model IDs (us., eu., etc.)"
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error listing models: {str(e)}"
        )


# Error handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    return {
        "error": "Not Found",
        "detail": "The requested endpoint does not exist",
        "path": str(request.url)
    }


@app.exception_handler(500)
async def internal_error_handler(request, exc):
    return {
        "error": "Internal Server Error",
        "detail": "An unexpected error occurred",
        "message": str(exc)
    }


# Startup event
@app.on_event("startup")
async def startup_event():
    """Run on application startup"""
    print("=" * 60)
    print("AWS Bedrock Chatbot API Starting...")
    print("=" * 60)
    print(f"📍 Region: {os.getenv('AWS_REGION', 'us-east-1')}")
    print(f"🤖 Default Model: {os.getenv('BEDROCK_MODEL_ID', 'us.amazon.nova-pro-v1:0')}")
    print(f"💾 DynamoDB Table: {os.getenv('DYNAMODB_TABLE_NAME', 'ChatbotConversations')}")
    print("=" * 60)
    print("💡 To change model: Edit BEDROCK_MODEL_ID in .env file")
    print("📚 API Documentation:")
    print("   - Swagger UI: http://localhost:8000/docs")
    print("   - ReDoc: http://localhost:8000/redoc")
    print("=" * 60)


@app.on_event("shutdown")
async def shutdown_event():
    """Run on application shutdown"""
    print("\n🛑 Shutting down API server...")
    # Clean up resources if needed


if __name__ == "__main__":
    import uvicorn
    
    # Run the API server
    uvicorn.run(
        "api:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # Auto-reload on code changes
        log_level="info"
    )

