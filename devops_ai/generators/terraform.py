"""Terraform infrastructure generator."""

from typing import Any, Dict, Optional

from .base import BaseGenerator


class TerraformGenerator(BaseGenerator):
    """Generate Terraform infrastructure as code."""

    TEMPLATES = {
        "vpc": """resource "aws_vpc" "main" {{
  cidr_block           = var.vpc_cidr
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = {{
    Name = "{project_name}-vpc"
  }}
}}

resource "aws_subnet" "public" {{
  vpc_id                  = aws_vpc.main.id
  cidr_block              = var.subnet_cidr
  availability_zone       = data.aws_availability_zones.available.names[0]
  map_public_ip_on_launch = true

  tags = {{
    Name = "{project_name}-public-subnet"
  }}
}}""",
        "rds": """resource "aws_db_instance" "main" {{
  identifier       = "{project_name}-db"
  engine           = "{engine}"
  engine_version   = var.db_engine_version
  instance_class   = var.db_instance_class
  allocated_storage = var.db_allocated_storage
  
  db_name  = var.db_name
  username = var.db_username
  password = random_password.db_password.result
  
  multi_az               = true
  publicly_accessible    = false
  skip_final_snapshot    = false
  final_snapshot_identifier = "{project_name}-final-snapshot"

  tags = {{
    Name = "{project_name}-db"
  }}
}}

resource "random_password" "db_password" {{
  length  = 16
  special = true
}}""",
        "eks": """resource "aws_eks_cluster" "main" {{
  name    = "{project_name}-cluster"
  version = var.kubernetes_version

  role_arn = aws_iam_role.eks_cluster.arn

  vpc_config {{
    subnet_ids = [aws_subnet.public.id]
    security_groups = [aws_security_group.cluster.id]
  }}

  depends_on = [
    aws_iam_role_policy_attachment.eks_cluster_policy,
  ]
}}

resource "aws_eks_node_group" "main" {{
  cluster_name    = aws_eks_cluster.main.name
  node_group_name = "{project_name}-node-group"
  node_role_arn   = aws_iam_role.eks_nodes.arn
  subnet_ids      = [aws_subnet.public.id]

  scaling_config {{
    desired_size = var.node_desired_size
    max_size     = var.node_max_size
    min_size     = var.node_min_size
  }}
}}""",
    }

    def generate(self, requirements: str) -> str:
        """Generate Terraform configuration from requirements."""
        if not self.validate_input(requirements):
            return "# Error: Invalid requirements"

        requirements_lower = requirements.lower()
        components = []

        # Detect infrastructure components
        if any(x in requirements_lower for x in ["vpc", "network", "networking"]):
            components.append(self._generate_vpc())

        if any(x in requirements_lower for x in ["database", "db", "rds", "postgres", "mysql"]):
            components.append(self._generate_rds(requirements_lower))

        if any(x in requirements_lower for x in ["kubernetes", "eks", "k8s"]):
            # Enterprise-grade EKS with autoscaling, security, and monitoring
            components.append(self._generate_security_groups())
            components.append(self._generate_iam_eks_roles())
            components.append(self._generate_eks_enhanced())
            components.append(self._generate_oidc_provider())
            components.append(self._generate_monitoring_infrastructure())

        if any(x in requirements_lower for x in ["lb", "load", "alb"]):
            components.append(self._generate_alb())

        if any(x in requirements_lower for x in ["s3", "storage", "bucket"]):
            components.append(self._generate_s3())

        # Add variables and outputs
        tf_config = self._generate_variables_extended() + "\n\n"
        tf_config += "\n\n".join(components)
        tf_config += "\n\n" + self._generate_outputs_extended()

        return tf_config

    def _generate_vpc(self) -> str:
        """Generate VPC configuration."""
        return self.TEMPLATES["vpc"].format(project_name=self.project_name)

    def _generate_rds(self, requirements: str) -> str:
        """Generate RDS configuration."""
        engine = "postgres"
        if "mysql" in requirements:
            engine = "mysql"
        elif "mariadb" in requirements:
            engine = "mariadb"

        return self.TEMPLATES["rds"].format(project_name=self.project_name, engine=engine)

    def _generate_eks(self) -> str:
        """Generate EKS configuration."""
        return self.TEMPLATES["eks"].format(project_name=self.project_name)

    def _generate_eks_enhanced(self) -> str:
        """Generate enhanced EKS cluster with monitoring and autoscaling."""
        return f"""# Enhanced EKS Cluster with enterprise-grade configuration

resource "aws_eks_cluster" "main" {{
  name    = "{self.project_name}-cluster"
  version = var.kubernetes_version
  role_arn = aws_iam_role.eks_cluster.arn

  vpc_config {{
    subnet_ids              = [aws_subnet.private_a.id, aws_subnet.private_b.id]
    security_groups         = [aws_security_group.eks_cluster.id]
    endpoint_private_access = true
    endpoint_public_access  = true
  }}

  # Enable CloudWatch logging
  enabled_cluster_log_types = ["api", "audit", "authenticator", "controllerManager", "scheduler"]

  depends_on = [
    aws_iam_role_policy_attachment.eks_cluster_policy,
    aws_iam_role_policy_attachment.eks_vpc_resource_controller,
  ]

  tags = {{
    Name = "{self.project_name}-cluster"
    Environment = "production"
  }}
}}

# CloudWatch Log Group for EKS
resource "aws_cloudwatch_log_group" "eks" {{
  name              = "/aws/eks/{self.project_name}-cluster/cluster"
  retention_in_days = 30

  tags = {{
    Name = "{self.project_name}-eks-logs"
  }}
}}

# Enhanced Node Group with Auto Scaling
resource "aws_eks_node_group" "main" {{
  cluster_name    = aws_eks_cluster.main.name
  node_group_name = "{self.project_name}-node-group"
  node_role_arn   = aws_iam_role.eks_nodes.arn
  subnet_ids      = [aws_subnet.private_a.id, aws_subnet.private_b.id]
  version         = var.kubernetes_version

  scaling_config {{
    desired_size = var.node_desired_size
    max_size     = var.node_max_size
    min_size     = var.node_min_size
  }}

  update_config {{
    max_unavailable_percentage = 33
  }}

  # Use optimized launch template
  launch_template {{
    id      = aws_launch_template.eks_nodes.id
    version = aws_launch_template.eks_nodes.latest_version_number
  }}

  labels = {{
    Environment = "production"
    ManagedBy   = "Terraform"
  }}

  depends_on = [
    aws_iam_role_policy_attachment.eks_node_policy,
    aws_iam_role_policy_attachment.eks_cni_policy,
    aws_iam_role_policy_attachment.eks_container_registry,
    aws_iam_role_policy_attachment.eks_ssm_policy,
  ]

  tags = {{
    Name = "{self.project_name}-node-group"
  }}
}}

# Optimized Launch Template for Nodes
resource "aws_launch_template" "eks_nodes" {{
  name_prefix = "{self.project_name}-"

  block_device_mappings {{
    device_name = "/dev/xvda"
    ebs {{
      volume_size           = var.node_volume_size
      volume_type           = "gp3"
      delete_on_termination = true
      encrypted             = true
    }}
  }}

  metadata_options {{
    http_endpoint               = "enabled"
    http_tokens                 = "required"
    http_put_response_hop_limit = 2
  }}

  monitoring {{
    enabled = true
  }}

  tag_specifications {{
    resource_type = "instance"
    tags = {{
      Name = "{self.project_name}-node"
    }}
  }}

  tag_specifications {{
    resource_type = "volume"
    tags = {{
      Name = "{self.project_name}-node-volume"
    }}
  }}
}}

# OIDC Provider for Workload Identity
resource "aws_iam_openid_connect_provider" "eks" {{
  client_id_list  = ["sts.amazonaws.com"]
  thumbprint_list = [data.tls_certificate.eks.certificates[0].sha1_fingerprint]
  url             = aws_eks_cluster.main.identity[0].oidc[0].issuer
}}

data "tls_certificate" "eks" {{
  url = aws_eks_cluster.main.identity[0].oidc[0].issuer
}}

# Cluster Autoscaler Service Account
resource "aws_iam_role" "cluster_autoscaler" {{
  name = "{self.project_name}-cluster-autoscaler"

  assume_role_policy = jsonencode({{
    Version = "2012-10-17"
    Statement = [
      {{
        Action = "sts:AssumeRoleWithWebIdentity"
        Effect = "Allow"
        Principal = {{
          Federated = aws_iam_openid_connect_provider.eks.arn
        }}
        Condition = {{
          StringEquals = {{
            "${{aws_iam_openid_connect_provider.eks.url}}:sub" = "system:serviceaccount:kube-system:cluster-autoscaler"
            "${{aws_iam_openid_connect_provider.eks.url}}:aud" = "sts.amazonaws.com"
          }}
        }}
      }}
    ]
  }})
}}

resource "aws_iam_role_policy" "cluster_autoscaler" {{
  name = "{self.project_name}-cluster-autoscaler"
  role = aws_iam_role.cluster_autoscaler.id

  policy = jsonencode({{
    Version = "2012-10-17"
    Statement = [
      {{
        Effect = "Allow"
        Action = [
          "autoscaling:DescribeAutoScalingGroups",
          "autoscaling:DescribeAutoScalingInstances",
          "autoscaling:DescribeLaunchConfigurations",
          "autoscaling:DescribeScalingActivities",
          "ec2:DescribeInstanceTypes",
          "ec2:DescribeLaunchTemplateVersions"
        ]
        Resource = "*"
      }},
      {{
        Effect = "Allow"
        Action = [
          "autoscaling:SetDesiredCapacity",
          "autoscaling:TerminateInstanceInAutoScalingGroup"
        ]
        Resource = "*"
        Condition = {{
          StringEquals = {{
            "autoscaling:ResourceTag/k8s.io/cluster-autoscaler/{self.project_name}" = "owned"
          }}
        }}
      }}
    ]
  }})
}}
"""

    def _generate_alb(self) -> str:
        """Generate Application Load Balancer configuration."""
        return """resource "aws_lb" "main" {
  name               = "{}-alb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.alb.id]
  subnets            = [aws_subnet.public.id]

  tags = {{
    Name = "{}-alb"
  }}
}}""".format(self.project_name, self.project_name)

    def _generate_s3(self) -> str:
        """Generate S3 bucket configuration."""
        return """resource "aws_s3_bucket" "main" {{
  bucket = "{}-bucket-${{random_string.bucket_suffix.result}}"

  tags = {{
    Name = "{}-bucket"
  }}
}}

resource "aws_s3_bucket_versioning" "main" {{
  bucket = aws_s3_bucket.main.id
  versioning_configuration {{
    status = "Enabled"
  }}
}}

resource "random_string" "bucket_suffix" {{
  length  = 8
  special = false
}}""".format(self.project_name, self.project_name)

    def _generate_security_groups(self) -> str:
        """Generate security groups with least privilege."""
        return f"""# Security Groups with least privilege principle

resource "aws_security_group" "eks_cluster" {{
  name        = "{self.project_name}-eks-cluster-sg"
  description = "Security group for EKS cluster control plane (least privilege)"
  vpc_id      = aws_vpc.main.id

  # Allow traffic from nodes
  ingress {{
    from_port       = 443
    to_port         = 443
    protocol        = "tcp"
    security_groups = [aws_security_group.eks_nodes.id]
    description     = "Allow nodes to communicate with cluster API"
  }}

  # Allow cluster to communicate with nodes
  egress {{
    from_port       = 0
    to_port         = 65535
    protocol        = "tcp"
    security_groups = [aws_security_group.eks_nodes.id]
    description     = "Allow cluster to communicate with nodes"
  }}

  egress {{
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
    description = "Allow outbound HTTPS for pulling container images"
  }}

  tags = {{
    Name = "{self.project_name}-eks-cluster-sg"
  }}
}}

resource "aws_security_group" "eks_nodes" {{
  name        = "{self.project_name}-eks-nodes-sg"
  description = "Security group for EKS nodes (least privilege)"
  vpc_id      = aws_vpc.main.id

  # Allow nodes to communicate with each other
  ingress {{
    from_port       = 0
    to_port         = 65535
    protocol        = "tcp"
    security_groups = [aws_security_group.eks_nodes.id]
    description     = "Allow node to node communication"
  }}

  # Allow cluster control plane to communicate with nodes
  ingress {{
    from_port       = 1025
    to_port         = 65535
    protocol        = "tcp"
    security_groups = [aws_security_group.eks_cluster.id]
    description     = "Allow cluster API to communicate with nodes"
  }}

  # Allow kubelet API
  ingress {{
    from_port       = 10250
    to_port         = 10250
    protocol        = "tcp"
    security_groups = [aws_security_group.eks_cluster.id]
    description     = "Allow kubelet API"
  }}

  egress {{
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
    description = "Allow outbound traffic"
  }}

  tags = {{
    Name = "{self.project_name}-eks-nodes-sg"
  }}
}}

resource "aws_security_group_rule" "nodes_alb" {{
  type                     = "ingress"
  from_port                = 80
  to_port                  = 80
  protocol                 = "tcp"
  security_group_id        = aws_security_group.eks_nodes.id
  source_security_group_id = aws_security_group.alb.id
  description              = "Allow ALB to communicate with nodes"
}}
"""

    def _generate_iam_eks_roles(self) -> str:
        """Generate IAM roles with least privilege for EKS."""
        return f"""# IAM Roles for EKS with least privilege

# EKS Cluster Role
resource "aws_iam_role" "eks_cluster" {{
  name = "{self.project_name}-eks-cluster-role"

  assume_role_policy = jsonencode({{
    Version = "2012-10-17"
    Statement = [
      {{
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {{
          Service = "eks.amazonaws.com"
        }}
      }}
    ]
  }})
}}

resource "aws_iam_role_policy_attachment" "eks_cluster_policy" {{
  policy_arn = "arn:aws:iam::aws:policy/AmazonEKSClusterPolicy"
  role       = aws_iam_role.eks_cluster.name
}}

resource "aws_iam_role_policy_attachment" "eks_vpc_resource_controller" {{
  policy_arn = "arn:aws:iam::aws:policy/AmazonEKSVPCResourceController"
  role       = aws_iam_role.eks_cluster.name
}}

# Custom policy for EKS cluster logging (least privilege)
resource "aws_iam_role_policy" "eks_cluster_logging" {{
  name = "{self.project_name}-eks-cluster-logging"
  role = aws_iam_role.eks_cluster.id

  policy = jsonencode({{
    Version = "2012-10-17"
    Statement = [
      {{
        Effect = "Allow"
        Action = [
          "logs:PutLogEvents",
          "logs:CreateLogStream"
        ]
        Resource = "arn:aws:logs:*:*:log-group:/aws/eks/{self.project_name}-*"
      }}
    ]
  }})
}}

# EKS Node Role
resource "aws_iam_role" "eks_nodes" {{
  name = "{self.project_name}-eks-node-role"

  assume_role_policy = jsonencode({{
    Version = "2012-10-17"
    Statement = [
      {{
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {{
          Service = "ec2.amazonaws.com"
        }}
      }}
    ]
  }})
}}

resource "aws_iam_role_policy_attachment" "eks_node_policy" {{
  policy_arn = "arn:aws:iam::aws:policy/AmazonEKSWorkerNodePolicy"
  role       = aws_iam_role.eks_nodes.name
}}

resource "aws_iam_role_policy_attachment" "eks_cni_policy" {{
  policy_arn = "arn:aws:iam::aws:policy/AmazonEKS_CNI_Policy"
  role       = aws_iam_role.eks_nodes.name
}}

resource "aws_iam_role_policy_attachment" "eks_container_registry" {{
  policy_arn = "arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryReadOnly"
  role       = aws_iam_role.eks_nodes.name
}}

# Custom policy for CloudWatch monitoring (least privilege)
resource "aws_iam_role_policy" "eks_node_monitoring" {{
  name = "{self.project_name}-eks-node-monitoring"
  role = aws_iam_role.eks_nodes.id

  policy = jsonencode({{
    Version = "2012-10-17"
    Statement = [
      {{
        Effect = "Allow"
        Action = [
          "cloudwatch:PutMetricData",
          "ec2:DescribeVolumes",
          "ec2:DescribeTags",
          "logs:PutLogEvents",
          "logs:CreateLogStream",
          "logs:CreateLogGroup"
        ]
        Resource = "*"
      }}
    ]
  }})
}}

# Add SSM policy for node access (optional but recommended)
resource "aws_iam_role_policy_attachment" "eks_ssm_policy" {{
  policy_arn = "arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore"
  role       = aws_iam_role.eks_nodes.name
}}

# Instance Profile for EC2
resource "aws_iam_instance_profile" "eks_nodes" {{
  name = "{self.project_name}-eks-node-profile"
  role = aws_iam_role.eks_nodes.name
}}
"""

    def _generate_oidc_provider(self) -> str:
        """Generate OIDC provider for workload identity."""
        return f"""# OIDC Provider for secure workload identity (IAM Roles for Service Accounts)

resource "aws_iam_openid_connect_provider" "eks_irsa" {{
  client_id_list  = ["sts.amazonaws.com"]
  thumbprint_list = [data.tls_certificate.eks_irsa.certificates[0].sha1_fingerprint]
  url             = aws_eks_cluster.main.identity[0].oidc[0].issuer

  tags = {{
    Name = "{self.project_name}-eks-irsa"
  }}
}}

data "tls_certificate" "eks_irsa" {{
  url = aws_eks_cluster.main.identity[0].oidc[0].issuer
}}
"""

    def _generate_monitoring_infrastructure(self) -> str:
        """Generate monitoring infrastructure with Prometheus and CloudWatch."""
        return f"""# Monitoring Infrastructure

# CloudWatch Log Group for application logs
resource "aws_cloudwatch_log_group" "eks_applications" {{
  name              = "/aws/eks/{self.project_name}-applications"
  retention_in_days = 30

  tags = {{
    Name = "{self.project_name}-app-logs"
  }}
}}

# CloudWatch Log Group for Prometheus
resource "aws_cloudwatch_log_group" "prometheus" {{
  name              = "/aws/eks/{self.project_name}-prometheus"
  retention_in_days = 30

  tags = {{
    Name = "{self.project_name}-prometheus-logs"
  }}
}}

# CloudWatch Dashboard for EKS monitoring
resource "aws_cloudwatch_dashboard" "eks" {{
  dashboard_name = "{self.project_name}-eks-dashboard"

  dashboard_body = jsonencode({{
    widgets = [
      {{
        type = "metric"
        properties = {{
          metrics = [
            ["AWS/EKS", "cluster_node_count", {{ stat = "Average" }}],
            [".", "cluster_cpu_usage", {{ stat = "Average" }}],
            [".", "cluster_memory_usage", {{ stat = "Average" }}],
            [".", "pods_running", {{ stat = "Average" }}]
          ]
          period = 60
          stat   = "Average"
          region = var.aws_region
          title  = "EKS Cluster Metrics"
        }}
      }}
    ]
  }})
}}

# SNS Topic for alarms
resource "aws_sns_topic" "eks_alerts" {{
  name = "{self.project_name}-eks-alerts"

  tags = {{
    Name = "{self.project_name}-eks-alerts"
  }}
}}

# CloudWatch Alarm for node CPU
resource "aws_cloudwatch_metric_alarm" "node_cpu_high" {{
  alarm_name          = "{self.project_name}-node-cpu-high"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "CPUUtilization"
  namespace           = "AWS/EC2"
  period              = "300"
  statistic           = "Average"
  threshold           = "80"
  alarm_description   = "Alert when node CPU exceeds 80%"
  alarm_actions       = [aws_sns_topic.eks_alerts.arn]
}}
"""

    def _generate_variables(self) -> str:
        """Generate variables file content."""
        return """variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "vpc_cidr" {
  description = "CIDR block for VPC"
  type        = string
  default     = "10.0.0.0/16"
}

variable "subnet_cidr" {
  description = "CIDR block for subnet"
  type        = string
  default     = "10.0.1.0/24"
}

variable "db_instance_class" {
  description = "Database instance class"
  type        = string
  default     = "db.t3.micro"
}

variable "db_allocated_storage" {
  description = "Database allocated storage (GB)"
  type        = number
  default     = 20
}

variable "db_engine_version" {
  description = "Database engine version"
  type        = string
  default     = "14.7"
}

variable "db_name" {
  description = "Database name"
  type        = string
  default     = "appdb"
}

variable "db_username" {
  description = "Database master username"
  type        = string
  default     = "admin"
  sensitive   = true
}

variable "kubernetes_version" {
  description = "Kubernetes version"
  type        = string
  default     = "1.28"
}

variable "node_desired_size" {
  description = "Desired number of worker nodes"
  type        = number
  default     = 3
}

variable "node_max_size" {
  description = "Maximum number of worker nodes"
  type        = number
  default     = 5
}

variable "node_min_size" {
  description = "Minimum number of worker nodes"
  type        = number
  default     = 1
}"""

    def _generate_variables_extended(self) -> str:
        """Generate extended variables with monitoring and security."""
        return self._generate_variables() + f"""

variable "node_volume_size" {{
  description = "Size of node volumes (GB)"
  type        = number
  default     = 50
}}

variable "enable_monitoring" {{
  description = "Enable Prometheus and monitoring"
  type        = bool
  default     = true
}}

variable "enable_logging" {{
  description = "Enable centralized logging"
  type        = bool
  default     = true
}}

variable "enable_cluster_autoscaler" {{
  description = "Enable cluster autoscaling"
  type        = bool
  default     = true
}}

variable "cloudwatch_log_retention" {{
  description = "CloudWatch log retention in days"
  type        = number
  default     = 30
}}

variable "enable_prometheus_grafana" {{
  description = "Enable Prometheus and Grafana stack"
  type        = bool
  default     = true
}}
"""

    def _generate_outputs(self) -> str:
        """Generate outputs file content."""
        return """output "vpc_id" {
  description = "VPC ID"
  value       = aws_vpc.main.id
}

output "subnet_id" {
  description = "Public Subnet ID"
  value       = aws_subnet.public.id
}

output "db_endpoint" {
  description = "Database endpoint"
  value       = try(aws_db_instance.main.endpoint, "")
}

output "eks_cluster_name" {
  description = "EKS cluster name"
  value       = try(aws_eks_cluster.main.name, "")
}

output "eks_cluster_endpoint" {
  description = "EKS cluster endpoint"
  value       = try(aws_eks_cluster.main.endpoint, "")
}"""

    def _generate_outputs_extended(self) -> str:
        """Generate extended outputs with monitoring and security info."""
        return self._generate_outputs() + f"""

# Enhanced EKS Outputs
output "eks_cluster_security_group_id" {{
  description = "Security group ID of the EKS cluster"
  value       = try(aws_security_group.eks_cluster.id, "")
}}

output "eks_node_security_group_id" {{
  description = "Security group ID of the EKS nodes"
  value       = try(aws_security_group.eks_nodes.id, "")
}}

output "eks_node_group_id" {{
  description = "EKS Node Group ID"
  value       = try(aws_eks_node_group.main.id, "")
}}

# IAM Outputs
output "eks_cluster_role_arn" {{
  description = "IAM role ARN for EKS cluster"
  value       = try(aws_iam_role.eks_cluster.arn, "")
}}

output "eks_node_role_arn" {{
  description = "IAM role ARN for EKS nodes"
  value       = try(aws_iam_role.eks_nodes.arn, "")
}}

output "cluster_autoscaler_role_arn" {{
  description = "IAM role ARN for Cluster Autoscaler"
  value       = try(aws_iam_role.cluster_autoscaler.arn, "")
}}

# Monitoring Outputs
output "eks_cluster_log_group_name" {{
  description = "CloudWatch log group for EKS cluster logs"
  value       = try(aws_cloudwatch_log_group.eks.name, "")
}}

output "cloudwatch_dashboard_url" {{
  description = "URL to EKS CloudWatch dashboard"
  value       = "https://console.aws.amazon.com/cloudwatch/home?region=${{var.aws_region}}#dashboards:name=${{aws_cloudwatch_dashboard.eks.dashboard_name}}"
}}

output "sns_topic_arn" {{
  description = "SNS topic ARN for EKS alerts"
  value       = try(aws_sns_topic.eks_alerts.arn, "")
}}

# OIDC Provider for Workload Identity
output "oidc_provider_arn" {{
  description = "ARN of the OIDC provider for EKS"
  value       = try(aws_iam_openid_connect_provider.eks_irsa.arn, "")
}}

output "oidc_provider_url" {{
  description = "URL of the OIDC provider"
  value       = try(aws_iam_openid_connect_provider.eks_irsa.url, "")
}}
"""
