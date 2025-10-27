# 📁 Project Structure

Clean and organized project structure for local development and AWS deployment.

## Directory Layout

```
d:\Works\Prac\langchain\
│
├── 📄 START_HERE.md              ← New users start here!
├── 📄 README.md                  ← Complete documentation
├── 📄 DEPLOYMENT_SUMMARY.md      ← Deployment quick reference
├── 📄 PROJECT_STRUCTURE.md       ← This file
│
├── 🐍 Core Application Files
│   ├── api.py                    ← FastAPI REST API server ⭐
│   ├── chatbot_aws.py            ← AWS Bedrock chatbot logic
│   ├── setup_dynamodb.py         ← DynamoDB table setup
│   ├── test_api_client.py        ← API testing client
│   └── requirements.txt          ← Python dependencies
│
├── 📂 deployment/                ← All deployment configurations
│   ├── README.md                 ← Deployment overview
│   ├── DEPLOY_LAMBDA.md          ← Lambda deployment guide
│   ├── DEPLOY_KUBERNETES.md      ← Kubernetes deployment guide
│   ├── ARCHITECTURE.md           ← System architecture
│   │
│   ├── 🐳 Docker Files
│   │   ├── Dockerfile            ← Standard Docker image
│   │   ├── Dockerfile.lambda     ← Lambda-specific image
│   │   ├── docker-compose.yml    ← Local Docker Compose
│   │   └── lambda_handler.py     ← Lambda function handler
│   │
│   ├── 🚀 Deployment Scripts
│   │   ├── deploy_lambda.sh      ← Lambda deploy (Linux/Mac)
│   │   ├── deploy_lambda.bat     ← Lambda deploy (Windows)
│   │   └── deploy_eks.sh         ← Kubernetes deploy (Linux/Mac)
│   │
│   ├── ☁️ CloudFormation
│   │   └── cloudformation_template.yaml  ← IaC template
│   │
│   └── ☸️ kubernetes/            ← Kubernetes manifests
│       ├── namespace.yaml        ← Namespace
│       ├── configmap.yaml        ← Configuration
│       ├── secret.yaml           ← Secrets template
│       ├── serviceaccount.yaml   ← Service account (IRSA)
│       ├── deployment.yaml       ← Pod deployment
│       ├── service.yaml          ← Internal service
│       ├── ingress.yaml          ← ALB ingress
│       ├── hpa.yaml              ← Auto-scaling
│       └── kustomization.yaml    ← Kustomize config
│
├── 📂 docs/                      ← Documentation
│   ├── API_EXAMPLES.md           ← API usage examples
│   ├── CHANGE_MODEL.md           ← Model configuration
│   ├── MODEL_IDS.md              ← Model ID reference ⭐
│   └── ENABLE_AMAZON_NOVA.md     ← AWS model setup
│
├── 📂 scripts/                   ← Helper scripts
│   ├── install.bat               ← Install dependencies (Windows)
│   └── run_api.bat               ← Quick start API (Windows)
│
└── 🔒 Configuration (Create these)
    ├── .env                      ← AWS credentials & config
    └── .gitignore                ← Git ignore rules
```

## File Purposes

### Core Files (Required)

| File | Purpose | Used For |
|------|---------|----------|
| `api.py` | FastAPI REST API server | Local & AWS Lambda & Kubernetes |
| `chatbot_aws.py` | AWS Bedrock integration | All deployments |
| `requirements.txt` | Python dependencies | All deployments |
| `.env` | AWS credentials & config | Local development |

### Deployment Files

| File | Purpose | Used For |
|------|---------|----------|
| `deployment/Dockerfile` | Standard Docker image | Local & Kubernetes |
| `deployment/Dockerfile.lambda` | Lambda container image | AWS Lambda only |
| `deployment/lambda_handler.py` | Lambda function handler | AWS Lambda only |
| `deployment/docker-compose.yml` | Local Docker environment | Local testing |
| `deployment/deploy_lambda.*` | Automated Lambda deployment | AWS Lambda |
| `deployment/deploy_eks.sh` | Automated EKS deployment | Kubernetes |
| `deployment/kubernetes/*` | Kubernetes manifests | Kubernetes only |

### Documentation Files

| File | Purpose |
|------|---------|
| `START_HERE.md` | Quick start guide for new users |
| `README.md` | Main project documentation |
| `DEPLOYMENT_SUMMARY.md` | Deployment options overview |
| `deployment/DEPLOY_LAMBDA.md` | Detailed Lambda guide |
| `deployment/DEPLOY_KUBERNETES.md` | Detailed Kubernetes guide |
| `deployment/ARCHITECTURE.md` | System architecture & design |
| `docs/MODEL_IDS.md` | Model ID reference (important!) |

### Helper Files

| File | Purpose | Platform |
|------|---------|----------|
| `scripts/install.bat` | Install dependencies | Windows |
| `scripts/run_api.bat` | Quick start API | Windows |
| `setup_dynamodb.py` | Create DynamoDB table | All |
| `test_api_client.py` | Test API client | All |

## What You Need For Each Deployment

### Local Development

**Required:**
- ✅ `api.py`
- ✅ `chatbot_aws.py`
- ✅ `requirements.txt`
- ✅ `.env` (create this)

**Optional:**
- `scripts/run_api.bat` (Windows quick start)
- `test_api_client.py` (testing)

**Run:**
```bash
python api.py
```

### Local Docker

**Required:**
- ✅ `api.py`
- ✅ `chatbot_aws.py`
- ✅ `requirements.txt`
- ✅ `deployment/Dockerfile`
- ✅ `deployment/docker-compose.yml`
- ✅ `.env` (create this)

**Run:**
```bash
docker-compose -f deployment/docker-compose.yml up
```

### AWS Lambda

**Required:**
- ✅ `api.py`
- ✅ `chatbot_aws.py`
- ✅ `requirements.txt`
- ✅ `deployment/Dockerfile.lambda`
- ✅ `deployment/lambda_handler.py`
- ✅ `deployment/deploy_lambda.sh` or `.bat`

**Run:**
```bash
cd deployment
./deploy_lambda.sh  # or deploy_lambda.bat
```

### Kubernetes (EKS)

**Required:**
- ✅ `api.py`
- ✅ `chatbot_aws.py`
- ✅ `requirements.txt`
- ✅ `deployment/Dockerfile`
- ✅ `deployment/kubernetes/*` (all manifests)
- ✅ `deployment/deploy_eks.sh`

**Run:**
```bash
cd deployment
export EKS_CLUSTER_NAME="your-cluster"
./deploy_eks.sh
```

## Configuration Files

### `.env` (Create this!)

```bash
AWS_ACCESS_KEY_ID=your_access_key_here
AWS_SECRET_ACCESS_KEY=your_secret_key_here
AWS_REGION=us-east-1
BEDROCK_MODEL_ID=us.amazon.nova-pro-v1:0
DYNAMODB_TABLE_NAME=ChatbotConversations
```

**Location:** Project root  
**Required for:** Local development, Docker Compose  
**Not needed for:** Lambda (uses IAM role), Kubernetes (uses secrets)

### `.gitignore`

Already configured to ignore:
- `__pycache__/` and `*.pyc`
- `.env` files
- Virtual environments
- IDE files
- Logs and databases

## File Sizes

Total project size: ~15 KB (code only)

```
Core Application:    ~8 KB
  ├─ api.py:         4.5 KB
  ├─ chatbot_aws.py: 3.2 KB
  └─ others:         0.3 KB

Deployment:          ~5 KB
  ├─ Dockerfiles:    2 KB
  ├─ K8s manifests:  2.5 KB
  └─ Scripts:        0.5 KB

Documentation:       150+ KB
  └─ Complete guides and examples
```

## Clean Architecture

### Separation of Concerns

```
┌─────────────────────────────────────────┐
│  Application Layer (Core Business Logic)│
│  ├─ api.py (REST API)                   │
│  └─ chatbot_aws.py (Chatbot Logic)      │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────▼───────────────────────┐
│  Deployment Layer (Infrastructure)      │
│  ├─ Docker (containers)                 │
│  ├─ Lambda (serverless)                 │
│  └─ Kubernetes (orchestration)          │
└─────────────────────────────────────────┘
```

### Why This Structure?

✅ **Clean Separation:** Core logic separate from deployment  
✅ **Reusable:** Same code runs in all environments  
✅ **Maintainable:** Easy to understand and modify  
✅ **Scalable:** Add new deployment methods easily  
✅ **Documented:** Comprehensive guides for everything  

## Deployment Method Selection

```
Start Here
    │
    ├─→ Testing locally? ──→ Use: docker-compose.yml
    │
    ├─→ MVP / Low traffic? ──→ Use: Lambda (deploy_lambda.sh)
    │
    └─→ Production / High traffic? ──→ Use: Kubernetes (deploy_eks.sh)
```

## Navigation Guide

### I want to...

**Get started quickly:**
→ Read `START_HERE.md`

**Understand the project:**
→ Read `README.md`

**Deploy to AWS:**
→ Read `DEPLOYMENT_SUMMARY.md`  
→ Choose: `deployment/DEPLOY_LAMBDA.md` or `deployment/DEPLOY_KUBERNETES.md`

**Understand architecture:**
→ Read `deployment/ARCHITECTURE.md`

**Use the API:**
→ Read `docs/API_EXAMPLES.md`

**Change the AI model:**
→ Read `docs/MODEL_IDS.md` ⭐ (Important!)  
→ Read `docs/CHANGE_MODEL.md`

**Set up AWS:**
→ Read `docs/ENABLE_AMAZON_NOVA.md`

## Keeping It Clean

### Do NOT commit:
- `.env` files with real credentials
- `__pycache__/` directories
- `.venv/` virtual environments
- IDE config files (`.vscode/`, `.idea/`)
- Log files
- Temporary files

### Do commit:
- All `.py` files
- All `.md` documentation
- All deployment configs
- `requirements.txt`
- `.gitignore`
- Example/template files

## Updates & Maintenance

### To update dependencies:
```bash
pip install --upgrade -r requirements.txt
```

### To rebuild Docker images:
```bash
# Local
docker-compose -f deployment/docker-compose.yml build

# Lambda
docker build -f deployment/Dockerfile.lambda -t chatbot-lambda .

# Kubernetes
docker build -f deployment/Dockerfile -t chatbot-api .
```

### To clean up:
```bash
# Remove Python cache
rmdir /s /q __pycache__

# Remove Docker images
docker system prune -a

# Remove virtual environment
rmdir /s /q .venv
```

---

## Quick Reference

| Task | Command |
|------|---------|
| **Install** | `pip install -r requirements.txt` |
| **Run Local** | `python api.py` |
| **Run Docker** | `docker-compose -f deployment/docker-compose.yml up` |
| **Deploy Lambda** | `cd deployment && deploy_lambda.bat` |
| **Deploy K8s** | `cd deployment && ./deploy_eks.sh` |
| **Test API** | `python test_api_client.py demo` |
| **Setup DB** | `python setup_dynamodb.py` |

---

**Questions?** Check `README.md` or specific deployment guides in `deployment/`

