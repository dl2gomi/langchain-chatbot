# 🚀 START HERE

Welcome! Get your chatbot API running in 5 minutes.

## Quick Setup

### 1. Install Dependencies (30 seconds)

```bash
# Windows
scripts\install.bat

# Or manually
pip install -r requirements.txt
```

### 2. Configure AWS (2 minutes)

Create a `.env` file in project root:

```bash
AWS_ACCESS_KEY_ID=your_access_key_here
AWS_SECRET_ACCESS_KEY=your_secret_key_here
AWS_REGION=us-east-1
BEDROCK_MODEL_ID=us.amazon.nova-pro-v1:0
DYNAMODB_TABLE_NAME=ChatbotConversations
```

**Don't have AWS keys?**
- Go to: https://console.aws.amazon.com/iam/
- Create a new user with programmatic access
- Attach these policies: `AmazonBedrockFullAccess`, `AmazonDynamoDBFullAccess`
- Copy the Access Key ID and Secret Access Key

### 3. Enable Amazon Nova (1 minute)

1. Go to: https://console.aws.amazon.com/bedrock/
2. Click "Model access" → "Manage model access"
3. Check: ✅ **Amazon Nova Pro** (instant approval, no forms!)
4. Click "Save changes"

### 4. Setup DynamoDB (30 seconds)

```bash
python setup_dynamodb.py
```

### 5. Start the API! (10 seconds)

```bash
# Windows
scripts\run_api.bat

# Or manually
python api.py
```

## 🎉 You're Done!

### Test Your API

**Open browser:** http://localhost:8000/docs

**Or use cURL:**
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello! What can you do?"}'
```

**Or use Python:**
```python
import requests
response = requests.post(
    "http://localhost:8000/chat",
    json={"message": "Hello!"}
)
print(response.json()['response'])
```

## 📚 What's Next?

### Learn More
- **Full Documentation:** [README.md](README.md)
- **API Examples:** [docs/API_EXAMPLES.md](docs/API_EXAMPLES.md)
- **Change Models:** [docs/CHANGE_MODEL.md](docs/CHANGE_MODEL.md)
- **Model IDs:** [docs/MODEL_IDS.md](docs/MODEL_IDS.md) ⭐

### Deploy to Production
- **Deployment Overview:** [docs/DEPLOYMENT_SUMMARY.md](docs/DEPLOYMENT_SUMMARY.md) - Quick reference
- **Deployment Guide:** [deployment/README.md](deployment/README.md) - Detailed guide
- **Docker:** `cd deployment && docker-compose up`
- **AWS Lambda:** See [deployment/DEPLOY_LAMBDA.md](deployment/DEPLOY_LAMBDA.md)
- **Kubernetes:** See [deployment/DEPLOY_KUBERNETES.md](deployment/DEPLOY_KUBERNETES.md)

### Test & Develop
```bash
# Interactive testing
python test_api_client.py interactive

# Run demo
python test_api_client.py demo
```

## 🆘 Having Issues?

### Common Problems

**"Cannot connect to AWS"**
- Check your `.env` file has correct credentials
- Run: `aws sts get-caller-identity` to verify

**"Access Denied for Bedrock"**
- Make sure you enabled Amazon Nova models in console
- Wait 2 minutes after enabling

**"DynamoDB Table Not Found"**
- Run: `python setup_dynamodb.py`

**"Port 8000 already in use"**
- Stop other processes using port 8000
- Or run: `uvicorn api:app --port 8001`

### Get Help

See [README.md](README.md#troubleshooting) for detailed troubleshooting.

---

**Ready to build amazing things! 🚀**

