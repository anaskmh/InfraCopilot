# InfraCopilot
## 🚀 Step-by-Step Demo Guide

This guide shows how anyone can install, run, and test **DevOps AI Copilot CLI**. It demonstrates how the tool automates real-world DevOps workflows using natural language.

---

## ✅ Prerequisites

Make sure the following are installed:

* Python 3.10+
* Git
* (Optional but recommended) Terraform, Docker, Kubectl

---

## ⚙️ 1. Installation

Clone the repository and install the CLI:

```bash
git clone https://github.com/<your-username>/devops-ai.git
cd devops-ai

python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

Verify installation:

```bash
devops-ai --help
```

---

## 📦 2. Initialize a New DevOps Project

Create a new project with recommended structure:

```bash
devops-ai init dev_challenge
cd dev_challenge
```

Check generated files:

```bash
ls
cat .devops-ai/config.json
```

---

## 🩺 3. System Health Check

Ensure required tools are available before deploying infrastructure:

```bash
devops-ai doctor
```

This checks:

* Terraform
* Kubernetes CLI
* Docker
* Git
* Python
* Optional tools like Docker Compose and jq

---

## ☁️ 4. Generate Terraform Infrastructure

Automatically create cloud infrastructure using natural language:

```bash
devops-ai generate terraform --desc "production AWS EKS cluster with autoscaling and monitoring"
```

Check generated files:

```bash
ls -R terraform
```

(Optional validation if Terraform is installed)

```bash
cd terraform
terraform fmt -check
terraform init -backend=false
terraform validate
cd ..
```

---

## ☸️ 5. Generate Kubernetes Deployment

```bash
devops-ai generate k8s --desc "deploy application with service, ingress, autoscaling"
```

Verify:

```bash
ls -R k8s
```

(Optional validation)

```bash
kubectl apply --dry-run=client -f k8s/
```

---

## 🐳 6. Generate Dockerfile

```bash
devops-ai generate docker --desc "secure production container with non-root user"
```

Verify:

```bash
cat Dockerfile
```

(Optional build)

```bash
docker build -t devops-ai-demo .
```

---

## 🔁 7. Generate CI/CD Pipeline

```bash
devops-ai generate github-workflows --desc "python CI with lint, test, docker build"
```

Verify:

```bash
ls github-workflows
cat github-workflows/ci.yml
```

---

## 📊 8. Generate Architecture Diagram

```bash
devops-ai diagram
```

Output:

```bash
cat outputs/architecture.mmd
```

---

## 🔍 9. Diagnose Infrastructure Issues

Create a sample log:

```bash
cat > error.log <<'EOF'
Warning  BackOff  kubelet  Back-off restarting failed container
Reason: CrashLoopBackOff
EOF
```

Run:

```bash
devops-ai diagnose error.log
```

This detects issues and suggests fixes.

---

## 💰 10. Cloud Cost Optimization

```bash
devops-ai cost
```

This analyzes Terraform files and suggests cost-saving improvements.

---

## 🤖 11. AI Self-Healing Recommendations

```bash
devops-ai heal
```

Provides:

* Infrastructure fixes
* Security improvements
* Performance optimizations

---

## 🎬 Recommended Demo Flow (5 Minutes)

For hackathons or presentations:

1. `devops-ai doctor`
2. `devops-ai init dev_challenge`
3. `generate terraform`
4. `generate k8s`
5. `diagram`
6. `diagnose`
7. `cost`
8. `heal`

---

## ⭐ Why This Matters

DevOps AI Copilot CLI helps developers:

* Automate repetitive DevOps tasks
* Reduce deployment time
* Improve reliability
* Optimize cloud costs
* Detect and fix issues faster
* Focus more on innovation instead of infrastructure

This tool boosts daily productivity by transforming natural language into production-ready DevOps workflows.

---

