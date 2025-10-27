# Correct Model IDs for AWS Bedrock

## Important: Use Region-Prefixed Model IDs

AWS Bedrock models require **region-prefixed** model IDs for on-demand throughput.

## ✅ Correct Model IDs

### Amazon Nova Models (Recommended)

```bash
# Use these IDs in your .env file:

# Nova Pro (balanced)
BEDROCK_MODEL_ID=us.amazon.nova-pro-v1:0

# Nova Lite (faster, cheaper)
BEDROCK_MODEL_ID=us.amazon.nova-lite-v1:0

# Nova Micro (fastest, cheapest)
BEDROCK_MODEL_ID=us.amazon.nova-micro-v1:0
```

### Anthropic Claude Models

```bash
# Claude 3.5 Sonnet (most capable)
BEDROCK_MODEL_ID=anthropic.claude-3-5-sonnet-20240620-v1:0

# Claude 3 Sonnet
BEDROCK_MODEL_ID=anthropic.claude-3-sonnet-20240229-v1:0

# Claude 3 Haiku (fast and cheap)
BEDROCK_MODEL_ID=anthropic.claude-3-haiku-20240307-v1:0
```

### Meta Llama Models

```bash
# Llama 3.2 90B
BEDROCK_MODEL_ID=meta.llama3-2-90b-instruct-v1:0

# Llama 3.1 70B
BEDROCK_MODEL_ID=meta.llama3-1-70b-instruct-v1:0

# Llama 3.1 8B
BEDROCK_MODEL_ID=meta.llama3-1-8b-instruct-v1:0
```

## ❌ Wrong Model IDs (Will Cause Errors)

```bash
# DON'T use these - they require inference profiles:
amazon.nova-pro-v1:0           # ❌ Missing region prefix
amazon.nova-premier-v1:0       # ❌ Requires inference profile ARN
amazon.nova-canvas-v1:0        # ❌ Image generation model
```

## Region-Specific Prefixes

Different regions use different prefixes:

| Region | Prefix | Example |
|--------|--------|---------|
| us-east-1 | `us.` | `us.amazon.nova-pro-v1:0` |
| us-west-2 | `us.` | `us.amazon.nova-pro-v1:0` |
| eu-west-1 | `eu.` | `eu.amazon.nova-pro-v1:0` |
| ap-southeast-1 | `apac.` | `apac.amazon.nova-pro-v1:0` |

**Note:** Claude and Llama models don't need region prefixes.

## How to Find Available Models

### Method 1: Use the API

```bash
curl -X POST http://localhost:8000/models/list
```

This returns all models available in your AWS account.

### Method 2: AWS Console

1. Go to: https://console.aws.amazon.com/bedrock/
2. Click "Providers" in sidebar
3. Browse available models
4. Click on a model to see its ID

### Method 3: AWS CLI

```bash
aws bedrock list-foundation-models \
  --region us-east-1 \
  --query 'modelSummaries[?contains(outputModalities, `TEXT`)].{ID:modelId, Name:modelName, Provider:providerName}' \
  --output table
```

## Common Errors and Solutions

### Error: "Invocation of model ID ... with on-demand throughput isn't supported"

**Problem:** Using wrong model ID format or a model that requires inference profile.

**Solution:** Use region-prefixed model IDs:
```bash
# Wrong
BEDROCK_MODEL_ID=amazon.nova-pro-v1:0

# Correct
BEDROCK_MODEL_ID=us.amazon.nova-pro-v1:0
```

### Error: "Could not resolve the foundation model"

**Problem:** Model ID doesn't exist or isn't available in your region.

**Solution:** 
1. Check available models: `POST /models/list`
2. Enable model access in AWS Console
3. Use correct region prefix

### Error: "Access denied"

**Problem:** Model not enabled in your AWS account.

**Solution:**
1. Go to AWS Bedrock Console
2. Click "Model access"
3. Enable the models you want to use

## Recommended Models by Use Case

### For Production (Balanced)
```bash
BEDROCK_MODEL_ID=us.amazon.nova-pro-v1:0
```
- Good quality
- Reasonable cost
- Fast enough
- No access form required

### For High Volume (Cost-Effective)
```bash
BEDROCK_MODEL_ID=us.amazon.nova-micro-v1:0
```
- Very cheap
- Very fast
- Good for simple queries

### For Best Quality (Expensive)
```bash
BEDROCK_MODEL_ID=anthropic.claude-3-5-sonnet-20240620-v1:0
```
- Highest quality responses
- Slower
- More expensive
- Requires access form

## Quick Test

Test your model ID:

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Hello!",
    "model_id": "us.amazon.nova-pro-v1:0"
  }'
```

If you get a valid response, the model ID is correct!

## More Information

- **AWS Bedrock Model IDs:** https://docs.aws.amazon.com/bedrock/latest/userguide/model-ids.html
- **Amazon Nova Documentation:** https://aws.amazon.com/bedrock/nova/
- **Pricing:** https://aws.amazon.com/bedrock/pricing/

---

**TL;DR:** Use `us.amazon.nova-pro-v1:0` (note the `us.` prefix) for Amazon Nova models!

