# API Usage Examples

Complete guide for using the Chatbot REST API

## Table of Contents
- [Quick Start](#quick-start)
- [API Endpoints](#api-endpoints)
- [cURL Examples](#curl-examples)
- [Python Examples](#python-examples)
- [JavaScript Examples](#javascript-examples)
- [Postman Collection](#postman-collection)

---

## Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Start the API Server
```bash
python api.py
```

Server will start at: **http://localhost:8000**

### 3. Access API Documentation
- **Swagger UI**: http://localhost:8000/docs (Interactive API testing)
- **ReDoc**: http://localhost:8000/redoc (Clean documentation)

---

## API Endpoints

### Base URL
```
http://localhost:8000
```

### Endpoints Overview

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | API information |
| GET | `/health` | Health check |
| POST | `/chat` | Send message to chatbot |
| GET | `/history/{session_id}` | Get conversation history |
| GET | `/session/{session_id}` | Get session information |
| GET | `/sessions` | List active sessions |
| DELETE | `/session/{session_id}` | Delete a session |
| POST | `/models/list` | List available models |

---

## cURL Examples

### 1. Health Check
```bash
curl http://localhost:8000/health
```

**Response:**
```json
{
  "status": "healthy",
  "service": "aws-bedrock-chatbot",
  "version": "1.0.0",
  "aws_region": "us-east-1",
  "timestamp": "2024-01-20T10:30:00.000Z"
}
```

### 2. Send a Message (New Session)
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What is AWS Lambda?"
  }'
```

**Response:**
```json
{
  "response": "AWS Lambda is a serverless compute service...",
  "session_id": "abc123-def456-ghi789",
  "model": "anthropic.claude-3-sonnet-20240229-v1:0",
  "region": "us-east-1",
  "timestamp": "2024-01-20T10:30:00.000Z"
}
```

### 3. Continue Conversation (Existing Session)
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Can you explain that in simpler terms?",
    "session_id": "abc123-def456-ghi789"
  }'
```

### 4. Get Conversation History
```bash
curl http://localhost:8000/history/abc123-def456-ghi789
```

**Response:**
```json
[
  {
    "timestamp": "2024-01-20T10:30:00.000Z",
    "role": "user",
    "content": "What is AWS Lambda?",
    "message_id": "msg-001"
  },
  {
    "timestamp": "2024-01-20T10:30:05.000Z",
    "role": "assistant",
    "content": "AWS Lambda is a serverless compute service...",
    "message_id": "msg-002"
  }
]
```

### 5. Get Session Info
```bash
curl http://localhost:8000/session/abc123-def456-ghi789
```

**Response:**
```json
{
  "session_id": "abc123-def456-ghi789",
  "region": "us-east-1",
  "model": "anthropic.claude-3-sonnet-20240229-v1:0",
  "user_messages": 2,
  "ai_messages": 2,
  "created_at": "2024-01-20T10:30:00.000Z"
}
```

### 6. List Active Sessions
```bash
curl http://localhost:8000/sessions
```

**Response:**
```json
[
  "abc123-def456-ghi789",
  "xyz789-uvw456-rst123"
]
```

### 7. Delete a Session
```bash
curl -X DELETE http://localhost:8000/session/abc123-def456-ghi789
```

**Response:**
```json
{
  "message": "Session abc123-def456-ghi789 deleted",
  "status": "success"
}
```

### 8. List Available Models
```bash
curl -X POST http://localhost:8000/models/list
```

**Response:**
```json
{
  "models": [
    {
      "id": "anthropic.claude-3-sonnet-20240229-v1:0",
      "name": "Claude 3 Sonnet",
      "description": "Balanced performance and cost",
      "cost": "medium"
    },
    {
      "id": "anthropic.claude-3-haiku-20240307-v1:0",
      "name": "Claude 3 Haiku",
      "description": "Fast and cost-effective",
      "cost": "low"
    }
  ]
}
```

### 9. Use Specific Model
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Explain quantum computing",
    "model_id": "anthropic.claude-3-haiku-20240307-v1:0"
  }'
```

---

## Python Examples

### Simple Chat Client
```python
import requests

# Base URL
API_URL = "http://localhost:8000"

# Send a message
response = requests.post(
    f"{API_URL}/chat",
    json={"message": "Hello! What can you do?"}
)

data = response.json()
print(f"Bot: {data['response']}")
print(f"Session ID: {data['session_id']}")

# Continue conversation
response2 = requests.post(
    f"{API_URL}/chat",
    json={
        "message": "Tell me more",
        "session_id": data['session_id']
    }
)

print(f"Bot: {response2.json()['response']}")
```

### Using the Test Client
```python
from test_api_client import ChatbotAPIClient

# Create client
client = ChatbotAPIClient()

# Send message
response = client.send_message("What is AWS Bedrock?")
print(response['response'])

# Continue conversation (same session)
response2 = client.send_message("How does it work?")
print(response2['response'])

# Get history
history = client.get_history()
for msg in history:
    print(f"{msg['role']}: {msg['content']}")
```

### Async Client
```python
import httpx
import asyncio

async def chat_async(message: str):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8000/chat",
            json={"message": message}
        )
        return response.json()

# Run
result = asyncio.run(chat_async("Hello!"))
print(result['response'])
```

---

## JavaScript Examples

### Using Fetch API
```javascript
// Send a message
async function sendMessage(message, sessionId = null) {
  const response = await fetch('http://localhost:8000/chat', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      message: message,
      session_id: sessionId
    })
  });
  
  return await response.json();
}

// Usage
const result = await sendMessage("What is AWS Lambda?");
console.log(result.response);
console.log("Session ID:", result.session_id);

// Continue conversation
const result2 = await sendMessage(
  "Tell me more",
  result.session_id
);
console.log(result2.response);
```

### Using Axios
```javascript
const axios = require('axios');

const API_URL = 'http://localhost:8000';

// Send message
axios.post(`${API_URL}/chat`, {
  message: 'Hello! What can you do?'
})
.then(response => {
  console.log('Bot:', response.data.response);
  console.log('Session ID:', response.data.session_id);
  
  // Continue conversation
  return axios.post(`${API_URL}/chat`, {
    message: 'Tell me more',
    session_id: response.data.session_id
  });
})
.then(response => {
  console.log('Bot:', response.data.response);
})
.catch(error => {
  console.error('Error:', error);
});
```

### React Example
```javascript
import React, { useState } from 'react';

function ChatComponent() {
  const [message, setMessage] = useState('');
  const [conversation, setConversation] = useState([]);
  const [sessionId, setSessionId] = useState(null);

  const sendMessage = async () => {
    const response = await fetch('http://localhost:8000/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        message: message,
        session_id: sessionId
      })
    });
    
    const data = await response.json();
    
    setConversation([
      ...conversation,
      { role: 'user', content: message },
      { role: 'assistant', content: data.response }
    ]);
    
    setSessionId(data.session_id);
    setMessage('');
  };

  return (
    <div>
      <div className="conversation">
        {conversation.map((msg, idx) => (
          <div key={idx} className={msg.role}>
            {msg.content}
          </div>
        ))}
      </div>
      <input
        value={message}
        onChange={(e) => setMessage(e.target.value)}
        placeholder="Type your message..."
      />
      <button onClick={sendMessage}>Send</button>
    </div>
  );
}
```

---

## Postman Collection

### Import to Postman

Create a new collection with these requests:

**1. Health Check**
- Method: `GET`
- URL: `{{base_url}}/health`

**2. Send Message**
- Method: `POST`
- URL: `{{base_url}}/chat`
- Body (JSON):
```json
{
  "message": "What is AWS Lambda?",
  "session_id": "{{session_id}}"
}
```

**3. Get History**
- Method: `GET`
- URL: `{{base_url}}/history/{{session_id}}`

**Environment Variables:**
- `base_url`: `http://localhost:8000`
- `session_id`: (will be set from response)

---

## Testing

### Using the Test Client

```bash
# Run conversation demo
python test_api_client.py demo

# Demo multiple sessions
python test_api_client.py sessions

# List available models
python test_api_client.py models

# Interactive chat mode
python test_api_client.py interactive
```

### Load Testing with Apache Bench
```bash
# Install Apache Bench
# Ubuntu: sudo apt-get install apache2-utils
# Mac: brew install apache2

# Simple load test
ab -n 100 -c 10 http://localhost:8000/health
```

### Load Testing with Locust
```bash
pip install locust

# Create locustfile.py
# Then run:
locust -f locustfile.py
```

---

## Error Handling

### Error Response Format
```json
{
  "detail": "Error message here"
}
```

### Common Error Codes

| Status Code | Description |
|-------------|-------------|
| 200 | Success |
| 400 | Bad Request (invalid input) |
| 404 | Not Found (session doesn't exist) |
| 500 | Internal Server Error |

### Example Error Handling (Python)
```python
import requests

try:
    response = requests.post(
        "http://localhost:8000/chat",
        json={"message": "Hello"}
    )
    response.raise_for_status()
    data = response.json()
    print(data['response'])
except requests.exceptions.HTTPError as e:
    print(f"HTTP Error: {e}")
    print(f"Response: {e.response.text}")
except Exception as e:
    print(f"Error: {e}")
```

---

## Rate Limiting (Future Enhancement)

Consider implementing rate limiting for production:

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.post("/chat")
@limiter.limit("10/minute")
async def chat(request: ChatRequest):
    # ...
```

---

## Authentication (Future Enhancement)

For production, add authentication:

```python
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()

@app.post("/chat")
async def chat(
    request: ChatRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    # Verify token
    # ...
```

---

## Best Practices

1. **Always handle errors gracefully**
2. **Store session_id for conversation continuity**
3. **Set reasonable timeouts on requests**
4. **Use environment variables for configuration**
5. **Implement retry logic for failed requests**
6. **Monitor API response times**
7. **Use HTTPS in production**
8. **Implement rate limiting**
9. **Add authentication/authorization**
10. **Log all API calls for debugging**

---

**Need Help?** See [README.md](README.md) or [README_AWS.md](README_AWS.md)

