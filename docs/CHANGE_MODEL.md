# How to Change AI Models

## Quick Guide

### Change Default Model (Affects All New Sessions)

**1. Edit your `.env` file:**
```bash
# Change this line:
BEDROCK_MODEL_ID=us.amazon.nova-pro-v1:0

# To any model you want:
BEDROCK_MODEL_ID=us.amazon.nova-lite-v1:0
```

**2. Restart the API:**
```bash
# Stop the server (Ctrl+C)
# Start it again:
python api.py
```

**3. Done!** All new chat sessions will use the new model.

---

## See All Available Models

### Method 1: API Endpoint
```bash
curl -X POST http://localhost:8000/models/list
```

This shows ALL models you have access to in AWS Bedrock (dynamically fetched from AWS).

### Method 2: AWS Console
1. Go to: https://console.aws.amazon.com/bedrock/
2. Click "Model access" in sidebar
3. See all models with "Access granted" status

---

## Change Model Per Request

You can override the default model for individual requests:

### cURL
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Hello!",
    "model_id": "us.amazon.nova-micro-v1:0"
  }'
```

### Python
```python
import requests

response = requests.post(
    "http://localhost:8000/chat",
    json={
        "message": "Hello!",
        "model_id": "amazon.nova-lite-v1:0"
    }
)
```

### JavaScript
```javascript
fetch('http://localhost:8000/chat', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    message: 'Hello!',
    model_id: 'anthropic.claude-3-haiku-20240307-v1:0'
  })
})
```

---

## Popular Model IDs

### Amazon Nova (No Form Required)
```bash
# Balanced - good for most tasks
BEDROCK_MODEL_ID=amazon.nova-pro-v1:0

# Fast - good for high volume
BEDROCK_MODEL_ID=amazon.nova-lite-v1:0

# Fastest - good for simple queries
BEDROCK_MODEL_ID=amazon.nova-micro-v1:0
```

### Anthropic Claude (Requires Access Form)
```bash
# Most capable
BEDROCK_MODEL_ID=anthropic.claude-3-opus-20240229-v1:0

# Balanced
BEDROCK_MODEL_ID=anthropic.claude-3-sonnet-20240229-v1:0

# Fast and cheap
BEDROCK_MODEL_ID=anthropic.claude-3-haiku-20240307-v1:0
```

### Meta Llama (Open Source)
```bash
# Large model
BEDROCK_MODEL_ID=meta.llama2-70b-chat-v1

# Medium model
BEDROCK_MODEL_ID=meta.llama2-13b-chat-v1
```

---

## Model Comparison

| Model | Speed | Cost | Quality | Access |
|-------|-------|------|---------|--------|
| Nova Micro | ⚡⚡⚡ | 💰 | ⭐⭐⭐ | Instant |
| Nova Lite | ⚡⚡ | 💰💰 | ⭐⭐⭐⭐ | Instant |
| Nova Pro | ⚡ | 💰💰💰 | ⭐⭐⭐⭐⭐ | Instant |
| Claude Haiku | ⚡⚡ | 💰💰 | ⭐⭐⭐⭐ | Form Required |
| Claude Sonnet | ⚡ | 💰💰💰 | ⭐⭐⭐⭐⭐ | Form Required |
| Claude Opus | 🐌 | 💰💰💰💰💰 | ⭐⭐⭐⭐⭐⭐ | Form Required |
| Llama2 70B | ⚡ | 💰💰 | ⭐⭐⭐⭐ | Instant |

---

## Configuration Priority

The model is selected in this order:

1. **Request parameter** (if provided in API call)
   ```json
   {"message": "...", "model_id": "amazon.nova-lite-v1:0"}
   ```

2. **Environment variable** (`.env` file)
   ```bash
   BEDROCK_MODEL_ID=amazon.nova-pro-v1:0
   ```

3. **Default fallback** (hardcoded)
   ```python
   # Default: amazon.nova-pro-v1:0
   ```

---

## Examples

### Example 1: Use Nova Lite by Default
```bash
# .env file
BEDROCK_MODEL_ID=amazon.nova-lite-v1:0
```

### Example 2: Switch Between Models
```python
import requests

API_URL = "http://localhost:8000/chat"

# Use Nova Micro for simple questions
simple_response = requests.post(API_URL, json={
    "message": "What is 2+2?",
    "model_id": "amazon.nova-micro-v1:0"
})

# Use Nova Pro for complex questions
complex_response = requests.post(API_URL, json={
    "message": "Explain quantum computing",
    "model_id": "amazon.nova-pro-v1:0"
})
```

### Example 3: A/B Testing Different Models
```python
models_to_test = [
    "amazon.nova-micro-v1:0",
    "amazon.nova-lite-v1:0",
    "amazon.nova-pro-v1:0"
]

for model in models_to_test:
    response = requests.post(API_URL, json={
        "message": "Tell me a joke",
        "model_id": model
    })
    print(f"\n{model}:")
    print(response.json()['response'])
```

---

## Troubleshooting

### "Model not found" Error
**Problem:** The model ID is incorrect or you don't have access.

**Solution:**
1. Check available models:
   ```bash
   curl -X POST http://localhost:8000/models/list
   ```
2. Enable access in AWS Console
3. Use exact model ID (case-sensitive)

### Model Still Using Old Default
**Problem:** You changed `.env` but API still uses old model.

**Solution:**
Restart the API server:
```bash
# Stop: Ctrl+C
# Start: python api.py
```

### How to Know Current Default?
```bash
# Check startup logs when running:
python api.py

# Look for:
# 🤖 Default Model: amazon.nova-pro-v1:0
```

### Get Current Model in Response
Every chat response includes the model used:
```json
{
  "response": "...",
  "session_id": "...",
  "model": "amazon.nova-pro-v1:0",  ← Current model
  "region": "us-east-1",
  "timestamp": "..."
}
```

---

## Best Practices

### 1. Use Fast Models for Simple Tasks
```python
# Use Micro for yes/no questions
# Use Lite for quick facts
# Use Pro for complex reasoning
```

### 2. Set Default to Most Common Use Case
```bash
# If 80% of requests are simple:
BEDROCK_MODEL_ID=amazon.nova-lite-v1:0

# If you need high quality:
BEDROCK_MODEL_ID=amazon.nova-pro-v1:0
```

### 3. Override for Special Cases
```python
# Default: Nova Lite
# But use Pro for important queries:
if is_important_query:
    model_id = "amazon.nova-pro-v1:0"
```

### 4. Monitor Costs
Different models have different costs. Check your AWS bill regularly.

---

## Summary

✅ **Change default:** Edit `BEDROCK_MODEL_ID` in `.env`
✅ **Per-request override:** Pass `model_id` in API call
✅ **See all models:** `POST /models/list`
✅ **Restart required:** After changing `.env`

**That's it! No code changes needed!** 🎉

