# 🧪 Testing Guide

Complete guide for testing your AWS Bedrock Chatbot in both local and AWS environments.

## Quick Tests

### 1. Local API Test (Fastest)

```bash
# Start the API
python api.py

# In another terminal, test it:
curl http://localhost:8000/health
```

**Expected:**
```json
{
  "status": "healthy",
  "service": "aws-bedrock-chatbot",
  "version": "1.0.0"
}
```

### 2. Send a Message

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello! What can you do?"}'
```

**Expected:**
```json
{
  "response": "Hello! I'm an AI assistant...",
  "session_id": "abc-123...",
  "model": "us.amazon.nova-pro-v1:0",
  "region": "us-east-1"
}
```

### 3. Check Available Models

```bash
curl -X POST http://localhost:8000/models/list
```

**Expected:**
```json
{
  "models": [
    {
      "id": "us.amazon.nova-pro-v1:0",
      "name": "Amazon Nova Pro",
      "provider": "Amazon"
    }
  ],
  "count": 3,
  "current_default": "us.amazon.nova-pro-v1:0"
}
```

## Using the Test Client

### Interactive Mode

```bash
python test_api_client.py interactive
```

Commands:
- Type any message to chat
- `history` - View conversation history
- `info` - View session information
- `new` - Start new session
- `quit` - Exit

### Demo Mode

```bash
python test_api_client.py demo
```

Runs automated tests:
1. Health check
2. First message
3. Follow-up message
4. Session info
5. Conversation history

### Multiple Sessions Demo

```bash
python test_api_client.py multi
```

Tests concurrent sessions.

### Models Demo

```bash
python test_api_client.py models
```

Lists all available models.

## Testing Each Deployment

### Local (Python)

**Start:**
```bash
python api.py
```

**Test:**
```bash
curl http://localhost:8000/health
```

**Expected:** ✅ Returns healthy status

---

### Local (Docker Compose)

**Start:**
```bash
docker-compose -f deployment/docker-compose.yml up
```

**Test:**
```bash
curl http://localhost:8000/health
```

**Expected:** ✅ Container running, API accessible

**Logs:**
```bash
docker-compose -f deployment/docker-compose.yml logs -f
```

**Stop:**
```bash
docker-compose -f deployment/docker-compose.yml down
```

---

### AWS Lambda

**Deploy:**
```bash
cd deployment
./deploy_lambda.sh  # or deploy_lambda.bat
```

**Test:**
```bash
# Get Function URL from deployment output
FUNCTION_URL="https://your-id.lambda-url.us-east-1.on.aws/"

# Health check
curl ${FUNCTION_URL}health

# Send message
curl -X POST ${FUNCTION_URL}chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello from Lambda!"}'
```

**Expected:** ✅ Lambda responds with valid JSON

**View Logs:**
```bash
aws logs tail /aws/lambda/chatbot-api --follow
```

**Metrics:**
```bash
aws cloudwatch get-metric-statistics \
  --namespace AWS/Lambda \
  --metric-name Invocations \
  --dimensions Name=FunctionName,Value=chatbot-api \
  --start-time $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 300 \
  --statistics Sum
```

---

### Kubernetes (EKS)

**Deploy:**
```bash
cd deployment
export EKS_CLUSTER_NAME="your-cluster"
./deploy_eks.sh
```

**Test (Port Forward):**
```bash
kubectl port-forward -n chatbot svc/chatbot-api 8000:80

# In another terminal:
curl http://localhost:8000/health
```

**Expected:** ✅ K8s service responds

**Test (Ingress):**
```bash
# Get ingress URL
INGRESS_URL=$(kubectl get ingress -n chatbot chatbot-ingress -o jsonpath='{.status.loadBalancer.ingress[0].hostname}')

curl http://${INGRESS_URL}/health
```

**View Logs:**
```bash
kubectl logs -n chatbot -l app=chatbot-api -f
```

**Check Pods:**
```bash
kubectl get pods -n chatbot
```

**Expected:**
```
NAME                          READY   STATUS    RESTARTS   AGE
chatbot-api-xxxxx-yyyyy       1/1     Running   0          2m
chatbot-api-xxxxx-zzzzz       1/1     Running   0          2m
chatbot-api-xxxxx-aaaaa       1/1     Running   0          2m
```

**Check HPA:**
```bash
kubectl get hpa -n chatbot
```

**Expected:**
```
NAME          REFERENCE                TARGETS   MINPODS   MAXPODS   REPLICAS
chatbot-hpa   Deployment/chatbot-api   20%/70%   2         10        3
```

## Load Testing

### Simple Load Test (curl-loader)

```bash
# Install hey (load testing tool)
# Windows: Download from https://github.com/rakyll/hey/releases
# Linux: go install github.com/rakyll/hey@latest

# Run load test
hey -n 1000 -c 10 http://localhost:8000/health
```

**Expected:**
```
Summary:
  Total:        5.2345 secs
  Slowest:      0.0234 secs
  Fastest:      0.0012 secs
  Average:      0.0052 secs
  Requests/sec: 191.12
```

### Python Load Test

```python
import concurrent.futures
import requests
import time

def send_request(i):
    try:
        response = requests.post(
            "http://localhost:8000/chat",
            json={"message": f"Test message {i}"}
        )
        return response.status_code == 200
    except Exception as e:
        return False

# Run 100 concurrent requests
with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
    start = time.time()
    results = list(executor.map(send_request, range(100)))
    duration = time.time() - start
    
    success_rate = sum(results) / len(results) * 100
    print(f"Duration: {duration:.2f}s")
    print(f"Success rate: {success_rate:.1f}%")
    print(f"Requests/sec: {len(results)/duration:.2f}")
```

**Expected:**
- Success rate: > 95%
- Requests/sec: > 10

## Testing AWS Services

### Test DynamoDB

```bash
python setup_dynamodb.py

# Verify table exists
aws dynamodb describe-table --table-name ChatbotConversations
```

**Expected:** Table status = ACTIVE

### Test Bedrock Access

```python
import boto3
import os
from dotenv import load_dotenv

load_dotenv()

bedrock = boto3.client(
    'bedrock',
    region_name=os.getenv("AWS_REGION", "us-east-1")
)

# List available models
response = bedrock.list_foundation_models()
print(f"Available models: {len(response['modelSummaries'])}")

for model in response['modelSummaries'][:3]:
    print(f"- {model['modelId']}: {model['modelName']}")
```

**Expected:** Lists available models

### Test Model Invocation

```python
import boto3
import json
import os
from dotenv import load_dotenv

load_dotenv()

bedrock_runtime = boto3.client(
    'bedrock-runtime',
    region_name=os.getenv("AWS_REGION", "us-east-1")
)

# Test with Nova Pro
response = bedrock_runtime.converse(
    modelId="us.amazon.nova-pro-v1:0",
    messages=[{
        "role": "user",
        "content": [{"text": "Hello!"}]
    }]
)

print("Response:", response['output']['message']['content'][0]['text'])
```

**Expected:** Returns AI response

## Troubleshooting Tests

### Test Fails: "Connection refused"

**Cause:** API not running

**Fix:**
```bash
# Check if API is running
# Windows:
netstat -ano | findstr :8000

# Linux/Mac:
lsof -i :8000

# Start API
python api.py
```

### Test Fails: "Access Denied" (Bedrock)

**Cause:** Model not enabled or wrong credentials

**Fix:**
1. Go to AWS Bedrock Console
2. Enable Amazon Nova models
3. Wait 2 minutes
4. Verify credentials in `.env`

```bash
aws sts get-caller-identity
```

### Test Fails: "DynamoDB Table Not Found"

**Cause:** Table not created

**Fix:**
```bash
python setup_dynamodb.py
```

### Test Fails: "Model ID not supported"

**Cause:** Wrong model ID format

**Fix:** Use region-prefixed IDs
```bash
# Wrong:
amazon.nova-pro-v1:0

# Correct:
us.amazon.nova-pro-v1:0
```

See `docs/MODEL_IDS.md` for details.

### Docker Test Fails: "Cannot connect to Docker daemon"

**Cause:** Docker not running

**Fix:**
```bash
# Windows: Start Docker Desktop
# Linux: sudo systemctl start docker
```

### Lambda Test Fails: "Function not found"

**Cause:** Lambda not deployed

**Fix:**
```bash
cd deployment
./deploy_lambda.sh
```

### Kubernetes Test Fails: "Connection refused"

**Cause:** Port forward not set up or ingress not ready

**Fix:**
```bash
# Use port forward
kubectl port-forward -n chatbot svc/chatbot-api 8000:80

# Or check ingress status
kubectl get ingress -n chatbot
```

## Test Checklist

### Local Development
- [ ] Python API starts without errors
- [ ] Health endpoint returns 200
- [ ] Can send chat message
- [ ] Can retrieve conversation history
- [ ] Model list endpoint works
- [ ] DynamoDB stores conversations

### Docker
- [ ] Docker image builds successfully
- [ ] Container starts without errors
- [ ] API accessible on port 8000
- [ ] Health check passes
- [ ] Chat functionality works

### AWS Lambda
- [ ] Lambda function deploys
- [ ] Function URL accessible
- [ ] Health check works
- [ ] Chat messages processed
- [ ] Logs appear in CloudWatch
- [ ] No timeout errors

### Kubernetes
- [ ] All pods running (3/3)
- [ ] Service accessible via port-forward
- [ ] Ingress configured (if using)
- [ ] HPA shows metrics
- [ ] Logs accessible
- [ ] Auto-scaling works

## Performance Benchmarks

### Expected Response Times

| Endpoint | Local | Lambda (cold) | Lambda (warm) | K8s |
|----------|-------|---------------|---------------|-----|
| `/health` | <10ms | 1-3s | <50ms | <20ms |
| `/chat` (Nova Micro) | 1-2s | 2-4s | 1-2s | 1-2s |
| `/chat` (Nova Pro) | 3-5s | 4-7s | 3-5s | 3-5s |
| `/history` | <100ms | 1-3s | <200ms | <150ms |
| `/models/list` | <1s | 1-4s | <1.5s | <1s |

### Memory Usage

| Deployment | Idle | Active |
|------------|------|--------|
| Local | 100MB | 250MB |
| Lambda | - | 512MB-1GB |
| Kubernetes (per pod) | 200MB | 400MB |

## Continuous Testing

### Set Up Monitoring

**CloudWatch Alarms (Lambda):**
```bash
aws cloudwatch put-metric-alarm \
  --alarm-name chatbot-errors \
  --comparison-operator GreaterThanThreshold \
  --evaluation-periods 1 \
  --metric-name Errors \
  --namespace AWS/Lambda \
  --period 60 \
  --statistic Sum \
  --threshold 5 \
  --dimensions Name=FunctionName,Value=chatbot-api
```

**Kubernetes Probes:**
Already configured in `deployment/kubernetes/deployment.yaml`:
- Liveness probe: `/health` every 10s
- Readiness probe: `/health` every 5s
- Startup probe: `/health` up to 300s

### Health Check Script

```bash
#!/bin/bash
# health_check.sh

ENDPOINT="http://localhost:8000"

while true; do
    RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" ${ENDPOINT}/health)
    
    if [ "$RESPONSE" -eq 200 ]; then
        echo "✅ $(date): Healthy"
    else
        echo "❌ $(date): Unhealthy (HTTP $RESPONSE)"
    fi
    
    sleep 30
done
```

## Summary

✅ **Local Testing:** `python api.py` + `curl http://localhost:8000/health`  
✅ **Docker Testing:** `docker-compose up` + test endpoints  
✅ **Lambda Testing:** Deploy + test Function URL  
✅ **Kubernetes Testing:** Deploy + port-forward + test  
✅ **Load Testing:** Use `hey` or Python script  
✅ **Monitoring:** CloudWatch + kubectl logs  

---

**Need help?** Check:
- `README.md` - Main documentation
- `docs/API_EXAMPLES.md` - API usage examples
- `deployment/` - Deployment guides

Happy testing! 🧪

