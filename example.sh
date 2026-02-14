#!/bin/bash
# Example script showing complete DevOps AI Copilot workflow

set -e

echo "======================================"
echo "DevOps AI Copilot - Complete Demo"
echo "======================================"

# Create project directory
PROJECT_DIR="example-devops-project"
rm -rf $PROJECT_DIR
mkdir -p $PROJECT_DIR
cd $PROJECT_DIR

echo ""
echo "1. Initializing DevOps project..."
devops-ai init backend-api --provider aws

echo ""
echo "2. Generating Terraform infrastructure (EKS + RDS)..."
devops-ai generate terraform \
  --desc "AWS EKS cluster with RDS PostgreSQL database and S3" \
  --project backend-api \
  --output terraform

echo ""
echo "3. Generating Kubernetes manifests..."
devops-ai generate k8s \
  --desc "deploy backend API with database, auto-scaling and monitoring" \
  --project backend-api \
  --output k8s

echo ""
echo "4. Generating Dockerfile..."
devops-ai generate docker \
  --desc "Python FastAPI application" \
  --project backend-api \
  --output docker

echo ""
echo "5. Generating GitHub Actions CI/CD workflow..."
devops-ai generate github-actions \
  --desc "test, build docker, deploy to EKS on main branch" \
  --project backend-api \
  --output github-workflows

echo ""
echo "6. Generating architecture diagrams..."
devops-ai diagram microservices --output ARCHITECTURE_MS.md
devops-ai diagram k8s --output ARCHITECTURE_K8S.md
devops-ai diagram pipeline --output CI_CD_PIPELINE.md

echo ""
echo "7. Cost optimization analysis..."
devops-ai cost --report > COST_OPTIMIZATION.md

echo ""
echo "======================================"
echo "✓ Project generated successfully!"
echo "======================================"
echo ""
echo "Generated files:"
ls -lh terraform/ k8s/ docker/ github-workflows/ 2>/dev/null | head -15
echo ""
echo "Diagrams and reports:"
ls -lh *.md 2>/dev/null || echo "No markdown files yet"
echo ""
echo "Next steps:"
echo "1. Review terraform/ directory"
echo "2. Review k8s/ directory for Kubernetes manifests"
echo "3. Review docker/ for Dockerfile configuration"
echo "4. Review github-workflows/ for CI/CD setup"
echo "5. Check COST_OPTIMIZATION.md for savings opportunities"
