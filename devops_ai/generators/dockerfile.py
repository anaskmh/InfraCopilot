"""Dockerfile generator."""

from .base import BaseGenerator


class DockerfileGenerator(BaseGenerator):
    """Generate Dockerfile configurations."""

    TEMPLATES = {
        "python": """FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \\
    build-essential \\
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY pyproject.toml* requirements*.txt* ./

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \\
    if [ -f pyproject.toml ]; then pip install --no-cache-dir -e .; else pip install --no-cache-dir -r requirements.txt; fi

# Copy application code
COPY . .

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=3s --start-period=40s --retries=3 \\
    CMD curl -f http://localhost:8080/health || exit 1

CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
""",
        "node": """FROM node:20-alpine

WORKDIR /app

# Install dependencies
COPY package*.json ./
RUN npm ci --only=production

# Copy application code
COPY . .

# Create non-root user
RUN addgroup -g 1000 appgroup && \\
    adduser -D -u 1000 -G appgroup appuser && \\
    chown -R appuser:appgroup /app
USER appuser

EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=3s --start-period=40s --retries=3 \\
    CMD wget --no-verbose --tries=1 --spider http://localhost:8080/health || exit 1

CMD ["node", "server.js"]
""",
        "go": """FROM golang:1.21-alpine AS builder

WORKDIR /build

# Install build dependencies
RUN apk add --no-cache git

# Copy source
COPY . .

# Build application
RUN CGO_ENABLED=0 GOOS=linux go build -a -installsuffix cgo -o app .

# Final stage
FROM alpine:3.18

RUN apk --no-cache add ca-certificates curl

WORKDIR /app

# Copy binary from builder
COPY --from=builder /build/app .

# Create non-root user
RUN addgroup -g 1000 appgroup && \\
    adduser -D -u 1000 -G appgroup appuser && \\
    chown -R appuser:appgroup /app
USER appuser

EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=3s --start-period=40s --retries=3 \\
    CMD curl -f http://localhost:8080/health || exit 1

CMD ["./app"]
""",
    }

    def generate(self, requirements: str) -> str:
        """Generate Dockerfile from requirements."""
        if not self.validate_input(requirements):
            return "# Error: Invalid requirements"

        requirements_lower = requirements.lower()

        # Detect language
        if "node" in requirements_lower or "javascript" in requirements_lower:
            dockerfile = self.TEMPLATES["node"]
        elif "go" in requirements_lower or "golang" in requirements_lower:
            dockerfile = self.TEMPLATES["go"]
        else:
            # Default to Python
            dockerfile = self.TEMPLATES["python"]

        # Add multi-stage considerations
        if "multi-stage" not in requirements_lower:
            return dockerfile

        return dockerfile

    def generate_multistage(self, requirements: str) -> str:
        """Generate multi-stage Dockerfile."""
        return """# Multi-stage Dockerfile for optimized images

FROM python:3.11 as builder

WORKDIR /build

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \\
    build-essential \\
    && rm -rf /var/lib/apt/lists/*

# Copy and install requirements
COPY pyproject.toml* requirements*.txt* ./
RUN pip install --user --no-cache-dir --upgrade pip && \\
    if [ -f pyproject.toml ]; then pip install --user --no-cache-dir -e .; else pip install --user --no-cache-dir -r requirements.txt; fi


# Final stage
FROM python:3.11-slim

WORKDIR /app

# Copy Python dependencies from builder
COPY --from=builder /root/.local /root/.local

# Update PATH
ENV PATH=/root/.local/bin:$PATH

# Copy application code
COPY . .

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=3s --start-period=40s --retries=3 \\
    CMD curl -f http://localhost:8080/health || exit 1

CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
"""

    def generate_dockercompose(self, requirements: str) -> str:
        """Generate docker-compose.yml."""
        return f"""version: '3.9'

services:
  {self.project_name}:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: {self.project_name}
    ports:
      - "8080:8080"
    environment:
      - ENVIRONMENT=production
      - LOG_LEVEL=INFO
      - DATABASE_URL=postgresql://user:password@postgres:5432/{self.project_name}
    depends_on:
      postgres:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080/health"]
      interval: 30s
      timeout: 3s
      retries: 3
      start_period: 40s
    restart: unless-stopped
    networks:
      - app-network

  postgres:
    image: postgres:15-alpine
    container_name: {self.project_name}-db
    environment:
      - POSTGRES_USER=dbuser
      - POSTGRES_PASSWORD=dbpassword
      - POSTGRES_DB={self.project_name}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U dbuser"]
      interval: 10s
      timeout: 5s
      retries: 5
    restart: unless-stopped
    networks:
      - app-network

  redis:
    image: redis:7-alpine
    container_name: {self.project_name}-cache
    ports:
      - "6379:6379"
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 3s
      retries: 3
    restart: unless-stopped
    networks:
      - app-network

volumes:
  postgres_data:

networks:
  app-network:
    driver: bridge
"""
