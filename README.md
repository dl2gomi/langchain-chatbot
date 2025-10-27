# AWS Bedrock Chatbot REST API 🤖

A production-ready REST API chatbot powered by **AWS Bedrock** (Amazon Nova AI), **DynamoDB**, and **FastAPI**.

## ✨ Features

- 🌐 **RESTful API** - FastAPI with automatic documentation (Swagger UI)
- 🤖 **Amazon Nova AI** - Fast, cost-effective, no access forms required
- 💾 **DynamoDB Storage** - Persistent conversation history
- 🔄 **Session Management** - Multi-user support
- ⚙️ **Easy Configuration** - Change models via `.env` file
- 📚 **Auto Documentation** - Built-in Swagger UI at `/docs`
- 🐳 **Docker Ready** - Containerized deployment
- ☁️ **AWS Lambda** - Serverless deployment option

## 🚀 Quick Start (5 Minutes)

### 1. Install Dependencies

```bash
# Windows
install.bat

# Manual
pip install -r requirements.txt
```

### 2. Configure AWS

**Option A: Create `.env` file** (Recommended)
```bash
AWS_ACCESS_KEY_ID=your_access_key_here
AWS_SECRET_ACCESS_KEY=your_secret_key_here
AWS_REGION=us-east-1
BEDROCK_MODEL_ID=us.amazon.nova-pro-v1:0
DYNAMODB_TABLE_NAME=ChatbotConversations
```

**Important:** Use region-prefixed model IDs (e.g., `us.amazon.nova-pro-v1:0` not `amazon.nova-pro-v1:0`)

**Option B: Use AWS CLI**
```bash
aws configure
```

### 3. Enable Amazon Nova in AWS Console

1. Go to: https://console.aws.amazon.com/bedrock/
2. Click **"Model access"** in sidebar
3. Click **"Manage model access"**
4. Check: ✅ **Amazon Nova Pro** (and optionally Lite/Micro)
5. Click **"Save changes"**
6. Wait 1-2 minutes (instant approval, no forms!)

### 4. Setup DynamoDB

```bash
python setup_dynamodb.py
```

### 5. Start the API!

```bash
python api.py
```

Server starts at: **http://localhost:8000**

### 6. Test It!

**Open your browser:** http://localhost:8000/docs

Or use cURL:
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello! What is AWS Bedrock?"}'
```

## 📖 API Documentation

### Interactive Documentation

Once the server is running:
- **Swagger UI:** http://localhost:8000/docs (Try it out!)
- **ReDoc:** http://localhost:8000/redoc (Clean docs)

### Main Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| POST | `/chat` | Send a message to the chatbot |
| GET | `/history/{session_id}` | Get conversation history |
| GET | `/sessions` | List active sessions |
| POST | `/models/list` | List available AWS Bedrock models |

### Example: Send a Message

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Explain AWS Lambda in simple terms"
  }'
```

Response:
```json
{
  "response": "AWS Lambda is a serverless compute service...",
  "session_id": "abc123-def456",
  "model": "amazon.nova-pro-v1:0",
  "region": "us-east-1",
  "timestamp": "2024-01-20T10:30:00Z"
}
```

## 🔧 Configuration

### Change AI Model

Edit `.env` file:
```bash
# Use Nova Lite (faster, cheaper)
BEDROCK_MODEL_ID=us.amazon.nova-lite-v1:0

# Use Nova Micro (fastest, cheapest)
BEDROCK_MODEL_ID=us.amazon.nova-micro-v1:0

# Use Nova Pro (balanced, default)
BEDROCK_MODEL_ID=us.amazon.nova-pro-v1:0
```

**Note:** Amazon Nova models require region-prefixed IDs (`us.`, `eu.`, etc.)

Restart the API after changing.

**See all available models:**
```bash
curl -X POST http://localhost:8000/models/list
```

### Override Model Per Request

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Hello!",
    "model_id": "us.amazon.nova-micro-v1:0"
  }'
```

## 🐍 Python Client

```python
import requests

# Send a message
response = requests.post(
    "http://localhost:8000/chat",
    json={"message": "What is AWS?"}
)

print(response.json()['response'])

# Continue conversation
response2 = requests.post(
    "http://localhost:8000/chat",
    json={
        "message": "Tell me more",
        "session_id": response.json()['session_id']
    }
)
```

### Test Client

We provide a ready-to-use test client:

```bash
# Run demo
python test_api_client.py demo

# Interactive chat mode
python test_api_client.py interactive

# Test multiple sessions
python test_api_client.py sessions

# List available models
python test_api_client.py models
```

## 📁 Project Structure

```
langchain/
├── api.py                    # Main FastAPI server ⭐
├── chatbot_aws.py            # AWS Bedrock integration
├── setup_dynamodb.py         # DynamoDB setup script
├── test_api_client.py        # Python API client
├── requirements.txt          # Python dependencies
├── .env                      # Configuration (create this)
├── .gitignore               # Git ignore rules
│
├── deployment/              # Deployment files
│   ├── Dockerfile           # Docker container
│   ├── docker-compose.yml   # Docker Compose
│   ├── lambda_handler.py    # AWS Lambda handler
│   ├── lambda_deploy.py     # Lambda deployment
│   └── cloudformation_template.yaml
│
├── docs/                    # Documentation
│   ├── API_EXAMPLES.md      # Complete API guide
│   ├── ENABLE_AMAZON_NOVA.md # AWS setup guide
│   └── CHANGE_MODEL.md      # Model configuration
│
└── scripts/                 # Helper scripts
    ├── run_api.bat          # Quick start (Windows)
    └── install.bat          # Dependency installer
```

## 🐳 Deployment

### Docker (Recommended for Production)

```bash
cd deployment
docker-compose up
```

Or manually:
```bash
docker build -f deployment/Dockerfile -t chatbot-api .
docker run -p 8000:8000 --env-file .env chatbot-api
```

### AWS Lambda (Serverless)

```bash
cd deployment
python lambda_deploy.py
```

Follow the prompts to deploy to AWS Lambda + API Gateway.

## 💰 Costs

### Amazon Nova Pricing (per 1,000 messages)

| Model | Cost/1K Messages | Speed | Quality |
|-------|------------------|-------|---------|
| Nova Micro | ~$0.17 | ⚡⚡⚡ | ⭐⭐⭐ |
| Nova Lite | ~$0.30 | ⚡⚡ | ⭐⭐⭐⭐ |
| Nova Pro | ~$4.00 | ⚡ | ⭐⭐⭐⭐⭐ |

**Plus:**
- DynamoDB: ~$0.05 per 1,000 messages
- API calls are free when testing locally

**Free Tier:**
- Lambda: 1M requests/month (forever!)
- DynamoDB: 25GB storage + 25 read/write capacity units

## 🐛 Troubleshooting

### "Cannot connect to AWS"
```bash
# Check your .env file
cat .env

# Or verify AWS credentials
aws sts get-caller-identity
```

### "Access Denied for Bedrock"
1. Go to: https://console.aws.amazon.com/bedrock/
2. Enable Amazon Nova models (instant approval!)
3. Wait 2 minutes and restart API

### "DynamoDB Table Not Found"
```bash
python setup_dynamodb.py
```

### "Port 8000 already in use"
```bash
# Windows: Find and kill the process
netstat -ano | findstr :8000
taskkill /PID <pid> /F

# Or use a different port
uvicorn api:app --port 8001
```

### API Returns Errors
1. Check logs in the terminal running `api.py`
2. Verify AWS credentials in `.env`
3. Ensure DynamoDB table exists
4. Confirm Bedrock models are enabled

## 📚 Documentation

- **API Examples:** [`docs/API_EXAMPLES.md`](docs/API_EXAMPLES.md)
- **Model Configuration:** [`docs/CHANGE_MODEL.md`](docs/CHANGE_MODEL.md)
- **Model IDs Reference:** [`docs/MODEL_IDS.md`](docs/MODEL_IDS.md) ⭐ (Important!)
- **AWS Setup:** [`docs/ENABLE_AMAZON_NOVA.md`](docs/ENABLE_AMAZON_NOVA.md)

## 🛠️ Development

### Running Locally

```bash
# Start API
python api.py

# In another terminal - test
python test_api_client.py interactive
```

### Environment Variables

Create a `.env` file:
```bash
AWS_ACCESS_KEY_ID=xxx
AWS_SECRET_ACCESS_KEY=xxx
AWS_REGION=us-east-1
BEDROCK_MODEL_ID=amazon.nova-pro-v1:0
DYNAMODB_TABLE_NAME=ChatbotConversations
```

### Requirements

- Python 3.8+
- AWS Account with Bedrock access
- AWS credentials configured

## 🌟 Why Amazon Nova?

✅ **No Access Forms** - Instant approval  
✅ **Lower Cost** - Up to 4x cheaper than alternatives  
✅ **Fast Performance** - Quick responses  
✅ **Multimodal** - Nova Pro supports images  
✅ **Built by AWS** - Native integration  

## 🔗 Links

- **AWS Bedrock:** https://aws.amazon.com/bedrock/
- **FastAPI Docs:** https://fastapi.tiangolo.com/
- **LangChain:** https://python.langchain.com/

## 📝 License

MIT License - Feel free to use and modify!

## 🤝 Contributing

Suggestions and improvements welcome! Key areas:

- [ ] Streaming responses
- [ ] Authentication/Authorization
- [ ] Rate limiting
- [ ] Response caching
- [ ] Multi-modal support (images)
- [ ] Conversation summarization

---

**Built with AWS ☁️ | Powered by Amazon Nova 🤖 | Production-Ready 🚀**

**Quick Start:** `install.bat` → Configure `.env` → `python api.py` → Visit http://localhost:8000/docs
