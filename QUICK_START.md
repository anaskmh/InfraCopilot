# 🚀 Quick Start Guide - DevOps AI Copilot

## Installation (30 seconds)

```bash
cd /Users/anask/devops-ai-copilot
source venv/bin/activate
devops-ai --help
```

## 5 Key Commands

### 1️⃣ Initialize Project
```bash
devops-ai init my-project --provider aws
```

### 2️⃣ Generate Terraform
```bash
devops-ai generate terraform \
  --desc "EKS cluster with RDS PostgreSQL" \
  --project my-project
```

### 3️⃣ Generate Kubernetes
```bash
devops-ai generate k8s \
  --desc "deploy microservices with auto-scaling" \
  --project my-project
```

### 4️⃣ Generate CI/CD
```bash
devops-ai generate github-actions \
  --desc "test, build docker, deploy to eks" \
  --project my-project
```

### 5️⃣ Get Cost Recommendations
```bash
devops-ai cost --report
```

## Other Useful Commands

```bash
# Generate Docker configuration
devops-ai generate docker --desc "python fastapi app" --project my-project

# Analyze logs
devops-ai diagnose --file app.log

# Generate architecture diagram
devops-ai diagram microservices --output architecture.md
```

## Files to Review

- **README.md** - Full documentation (12KB)
- **IMPLEMENTATION_SUMMARY.md** - Technical details
- **CHANGELOG.md** - Version history
- **example.sh** - Full end-to-end example

## Run Example

```bash
bash example.sh
```

## Run Tests

```bash
source venv/bin/activate
pytest tests/ -v --cov=devops_ai
```

## What You Get

✅ **Instant Infrastructure Code**
- Terraform HCL
- Kubernetes YAML
- Dockerfile & docker-compose
- GitHub Actions workflows

✅ **Smart Diagnostics**
- Log error pattern detection
- Fix suggestions
- Infrastructure health checks

✅ **Cost Optimization**
- 8 actionable recommendations
- Priority-based analysis
- Detailed implementation steps

✅ **Architecture Diagrams**
- Microservices
- Monolith
- Serverless
- Hybrid cloud
- Kubernetes
- CI/CD pipeline

## Project Structure

```
├── devops_ai/          # Main Python package
│   ├── generators/     # Terraform, K8s, Docker, GitHub Actions
│   ├── diagnostics/    # Log analysis
│   ├── cost/          # Cost optimization
│   ├── diagram/       # Architecture diagrams
│   └── utils.py       # Utilities
├── tests/             # 37 passing tests
├── README.md          # Full docs
└── example.sh         # Demo script
```

## Stats

- ✅ **37 Tests** (all passing)
- ✅ **21 Python modules**
- ✅ **625 lines** of core code
- ✅ **65% code coverage**
- ✅ **Zero external APIs** (offline)
- ✅ **Production ready**

## Next Steps

1. Try `devops-ai init test-project`
2. Generate some infrastructure
3. Check the output files
4. Run the tests
5. Review the code

Enjoy! 🎉
