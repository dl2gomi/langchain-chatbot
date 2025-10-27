# How to Enable Amazon Nova Models

## Good News! 🎉

**Amazon Nova models don't require filling out a use case form!** They're much easier to enable than Claude models.

## Quick Steps (2 minutes)

### 1. Go to AWS Bedrock Console
Open this link:
**https://us-east-1.console.aws.amazon.com/bedrock/home?region=us-east-1#/modelaccess**

### 2. Enable Amazon Nova Models

1. **Sign in** to your AWS account
2. Click **"Manage model access"** (orange button)
3. **Find and check these models:**
   - ✅ **Amazon Nova Pro** (recommended - default)
   - ✅ **Amazon Nova Lite** (faster, cheaper)
   - ✅ **Amazon Nova Micro** (fastest, cheapest)

4. **Click "Save changes"** at the bottom

5. **Wait 1-2 minutes** for instant approval

### 3. Test Your API

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello! What is AWS Bedrock?"}'
```

That's it! No forms to fill out! 🚀

---

## Amazon Nova Model Comparison

| Model | Speed | Cost | Best For |
|-------|-------|------|----------|
| **Nova Pro** | Medium | $$ | General chat, multimodal tasks (default) |
| **Nova Lite** | Fast | $ | Quick responses, high volume |
| **Nova Micro** | Very Fast | ¢ | Simple queries, maximum speed |

### Pricing (as of 2024)

**Amazon Nova Pro:**
- Input: $0.0008 per 1K tokens
- Output: $0.0032 per 1K tokens
- ~$0.004 per message

**Amazon Nova Lite:**
- Input: $0.00006 per 1K tokens
- Output: $0.00024 per 1K tokens
- ~$0.0003 per message

**Amazon Nova Micro:**
- Input: $0.000035 per 1K tokens
- Output: $0.00014 per 1K tokens
- ~$0.00017 per message

**Much cheaper than Claude!** 💰

---

## Verify Access

After enabling, verify with:

```bash
python setup_dynamodb.py
```

Look for:
```
✓ AWS Bedrock access confirmed (us-east-1)
  Available models: 50+
```

---

## Using Different Nova Models

### In API Requests

**Default (Nova Pro):**
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello!"}'
```

**Using Nova Lite (faster):**
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Hello!",
    "model_id": "amazon.nova-lite-v1:0"
  }'
```

**Using Nova Micro (fastest/cheapest):**
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Hello!",
    "model_id": "amazon.nova-micro-v1:0"
  }'
```

### In Python Client

```python
import requests

# Using Nova Pro (default)
response = requests.post(
    "http://localhost:8000/chat",
    json={"message": "Hello!"}
)

# Using Nova Lite
response = requests.post(
    "http://localhost:8000/chat",
    json={
        "message": "Hello!",
        "model_id": "amazon.nova-lite-v1:0"
    }
)
```

### Change Default Model

Edit `.env` file:
```bash
BEDROCK_MODEL_ID=amazon.nova-lite-v1:0
```

Or in `chatbot_aws.py`:
```python
bot = AWSChatbot(model_id="amazon.nova-lite-v1:0")
```

---

## Why Choose Amazon Nova?

✅ **No access forms required** - instant approval
✅ **Lower cost** - cheaper than Claude
✅ **Fast performance** - quick responses
✅ **Multimodal** - Nova Pro supports images
✅ **Built by AWS** - native integration
✅ **Multiple tiers** - choose speed vs cost

---

## Regional Availability

Amazon Nova is available in:
- ✅ **us-east-1** (Virginia)
- ✅ **us-west-2** (Oregon)
- ✅ **eu-west-1** (Ireland)
- ✅ **ap-southeast-1** (Singapore)

Default region is **us-east-1**.

---

## Troubleshooting

### Still getting "ResourceNotFoundException"?

1. **Wait 2 minutes** after enabling
2. **Restart your API:**
   ```bash
   # Stop with Ctrl+C
   python api.py
   ```
3. **Check model is enabled:**
   - Go back to Bedrock console
   - Verify "Access granted" status

### "Model not found"?

Check the exact model ID:
```python
# Correct ✓
"amazon.nova-pro-v1:0"

# Wrong ✗
"amazon.nova-pro"
"amazon-nova-pro-v1:0"
```

### Need help?

Run diagnostics:
```bash
python setup_dynamodb.py
```

This will check:
- AWS credentials
- Bedrock access
- Available models
- DynamoDB connection

---

## Next Steps

Once Nova models are enabled:

1. ✅ Test the API
2. ✅ Build your frontend
3. ✅ Deploy to production
4. ✅ Monitor costs (much lower than Claude!)

---

**Your chatbot is now using Amazon Nova! Much easier and cheaper! 🚀💰**

