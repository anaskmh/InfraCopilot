"""Cost optimization analyzer."""

from typing import Dict, List


class CostOptimizer:
    """Analyze and suggest cost optimization."""

    # Cost optimization rules
    OPTIMIZATION_RULES = {
        "rightsizing": {
            "title": "Instance Rightsizing",
            "description": "Use smaller instance types for underutilized resources",
            "savings": "20-40%",
            "effort": "Medium",
            "priority": "High",
            "actions": [
                "Analyze historical CPU and memory usage",
                "Right-size instances based on actual needs",
                "Use burstable instance types for variable workloads",
            ],
        },
        "reserved_instances": {
            "title": "Reserved Instances",
            "description": "Purchase reserved instances for predictable workloads",
            "savings": "30-70%",
            "effort": "Low",
            "priority": "High",
            "actions": [
                "Identify long-running instances (>70% uptime)",
                "Purchase 1-year or 3-year reserved instances",
                "Use savings plans for compute flexibility",
            ],
        },
        "spot_instances": {
            "title": "Spot Instances",
            "description": "Use spot instances for fault-tolerant workloads",
            "savings": "60-90%",
            "effort": "High",
            "priority": "Medium",
            "actions": [
                "Identify batch and fault-tolerant workloads",
                "Implement spot interruption handling",
                "Mix on-demand and spot instances",
            ],
        },
        "storage_optimization": {
            "title": "Storage Optimization",
            "description": "Optimize storage tier and retention",
            "savings": "30-50%",
            "effort": "Medium",
            "priority": "High",
            "actions": [
                "Transition cold data to cheaper tiers",
                "Enable S3 Intelligent-Tiering",
                "Review and clean up unattached volumes",
                "Implement lifecycle policies",
            ],
        },
        "networking": {
            "title": "Network Optimization",
            "description": "Reduce data transfer costs",
            "savings": "20-30%",
            "effort": "Medium",
            "priority": "Medium",
            "actions": [
                "Use VPC endpoints instead of NAT gateways",
                "Optimize data transfer between regions",
                "Consolidate NAT gateways",
            ],
        },
        "database_optimization": {
            "title": "Database Optimization",
            "description": "Optimize database resources",
            "savings": "25-40%",
            "effort": "High",
            "priority": "High",
            "actions": [
                "Use Multi-AZ selectively (only for production)",
                "Archive old data to cheaper storage",
                "Optimize query performance",
                "Use read replicas instead of larger instances",
            ],
        },
        "container_efficiency": {
            "title": "Container Efficiency",
            "description": "Optimize Kubernetes resource usage",
            "savings": "20-35%",
            "effort": "Medium",
            "priority": "Medium",
            "actions": [
                "Set appropriate resource requests and limits",
                "Use HPA with proper thresholds",
                "Bin packing workloads efficiently",
                "Monitor and adjust over time",
            ],
        },
        "unused_resources": {
            "title": "Remove Unused Resources",
            "description": "Identify and remove unused resources",
            "savings": "10-20%",
            "effort": "Low",
            "priority": "High",
            "actions": [
                "Audit and remove unattached EBS volumes",
                "Delete unused snapshots",
                "Remove unused load balancers",
                "Clean up idle Elastic IPs",
            ],
        },
    }

    def analyze_infrastructure(self, infrastructure_config: Dict) -> Dict:
        """Analyze infrastructure for cost optimization."""
        recommendations = []

        for rule_key, rule in self.OPTIMIZATION_RULES.items():
            recommendation = {
                "id": rule_key,
                "title": rule["title"],
                "description": rule["description"],
                "estimated_savings": rule["savings"],
                "effort": rule["effort"],
                "priority": rule["priority"],
                "actions": rule["actions"],
            }
            recommendations.append(recommendation)

        # Sort by priority
        priority_order = {"High": 0, "Medium": 1, "Low": 2}
        recommendations.sort(key=lambda x: priority_order.get(x["priority"], 3))

        return {
            "total_recommendations": len(recommendations),
            "high_priority": sum(1 for r in recommendations if r["priority"] == "High"),
            "recommendations": recommendations,
        }

    def estimate_monthly_savings(self, recommendations: List[Dict]) -> float:
        """Estimate monthly savings from recommendations."""
        # This is a simplified estimate
        savings_percentages = {
            "rightsizing": 30,
            "reserved_instances": 50,
            "spot_instances": 75,
            "storage_optimization": 40,
            "networking": 25,
            "database_optimization": 32,
            "container_efficiency": 27,
            "unused_resources": 15,
        }

        total_savings = sum(savings_percentages.get(r["id"], 0) for r in recommendations) / len(
            recommendations
        ) if recommendations else 0

        return total_savings

    def generate_cost_report(self, infrastructure_config: Dict) -> str:
        """Generate cost optimization report."""
        analysis = self.analyze_infrastructure(infrastructure_config)
        report = "# DevOps AI - Cost Optimization Report\n\n"
        report += f"## Summary\n"
        report += f"- Total Recommendations: {analysis['total_recommendations']}\n"
        report += f"- High Priority: {analysis['high_priority']}\n\n"

        report += "## Recommendations\n\n"
        for idx, rec in enumerate(analysis["recommendations"], 1):
            report += f"### {idx}. {rec['title']}\n"
            report += f"**Priority:** {rec['priority']} | **Effort:** {rec['effort']} | **Savings:** {rec['estimated_savings']}\n\n"
            report += f"{rec['description']}\n\n"
            report += "**Actions:**\n"
            for action in rec["actions"]:
                report += f"- {action}\n"
            report += "\n"

        return report
