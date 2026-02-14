"""Architecture diagram generator using Mermaid."""

from typing import Dict, List


class DiagramGenerator:
    """Generate architecture diagrams using Mermaid."""

    def generate_architecture(self, architecture_type: str = "microservices") -> str:
        """Generate architecture diagram."""
        diagrams = {
            "microservices": self._generate_microservices_diagram,
            "monolith": self._generate_monolith_diagram,
            "serverless": self._generate_serverless_diagram,
            "hybrid": self._generate_hybrid_diagram,
        }

        generator = diagrams.get(architecture_type, self._generate_microservices_diagram)
        return generator()

    def _generate_microservices_diagram(self) -> str:
        """Generate microservices architecture diagram."""
        return """graph TB
    subgraph "Client Layer"
        Web["🌐 Web Client"]
        Mobile["📱 Mobile Client"]
    end

    subgraph "API Gateway & Load Balancing"
        LB["⚖️ Load Balancer"]
        Gateway["🚪 API Gateway"]
    end

    subgraph "Microservices"
        AuthSvc["🔐 Auth Service"]
        UserSvc["👤 User Service"]
        OrderSvc["📦 Order Service"]
        PaymentSvc["💳 Payment Service"]
    end

    subgraph "Data Layer"
        AuthDB["🗄️ Auth DB"]
        UserDB["🗄️ User DB"]
        OrderDB["🗄️ Order DB"]
        Cache["💾 Cache/Redis"]
    end

    subgraph "Message Queue"
        Queue["📨 Message Queue"]
    end

    subgraph "External Services"
        PaymentGW["🏦 Payment Gateway"]
        Email["📧 Email Service"]
    end

    Web --> LB
    Mobile --> LB
    LB --> Gateway
    Gateway --> AuthSvc
    Gateway --> UserSvc
    Gateway --> OrderSvc

    AuthSvc --> AuthDB
    UserSvc --> UserDB
    OrderSvc --> OrderDB
    OrderSvc --> Cache
    
    OrderSvc --> Queue
    PaymentSvc --> Queue
    PaymentSvc --> PaymentGW
    Queue --> Email

    style Web fill:#e1f5ff
    style Mobile fill:#e1f5ff
    style Gateway fill:#fff3e0
    style AuthSvc fill:#f3e5f5
    style UserSvc fill:#f3e5f5
    style OrderSvc fill:#f3e5f5
    style PaymentSvc fill:#f3e5f5
    style AuthDB fill:#e8f5e9
    style UserDB fill:#e8f5e9
    style OrderDB fill:#e8f5e9
    style Cache fill:#fce4ec
"""

    def _generate_monolith_diagram(self) -> str:
        """Generate monolithic architecture diagram."""
        return """graph TB
    subgraph "Client Layer"
        Web["🌐 Web Client"]
        Mobile["📱 Mobile Client"]
    end

    subgraph "Load Balancing"
        LB["⚖️ Load Balancer"]
    end

    subgraph "Application Servers"
        App1["🖥️ App Instance 1"]
        App2["🖥️ App Instance 2"]
        App3["🖥️ App Instance 3"]
    end

    subgraph "Data Layer"
        DB["🗄️ Primary Database"]
        DBReplica["🗄️ Read Replica"]
        Cache["💾 Cache"]
    end

    subgraph "External Services"
        Email["📧 Email"]
        Storage["☁️ Cloud Storage"]
    end

    Web --> LB
    Mobile --> LB
    LB --> App1
    LB --> App2
    LB --> App3

    App1 --> DB
    App2 --> DB
    App3 --> DB
    
    App1 --> DBReplica
    App2 --> DBReplica
    App3 --> DBReplica
    
    App1 --> Cache
    App2 --> Cache
    App3 --> Cache

    App1 --> Email
    App2 --> Email
    App3 --> Email
    
    App1 --> Storage
    App2 --> Storage
    App3 --> Storage

    style Web fill:#e1f5ff
    style Mobile fill:#e1f5ff
    style App1 fill:#f3e5f5
    style App2 fill:#f3e5f5
    style App3 fill:#f3e5f5
    style DB fill:#e8f5e9
    style DBReplica fill:#e8f5e9
    style Cache fill:#fce4ec
"""

    def _generate_serverless_diagram(self) -> str:
        """Generate serverless architecture diagram."""
        return """graph TB
    subgraph "Client"
        Web["🌐 Web/Mobile"]
    end

    subgraph "API & Edge"
        CDN["🚀 CDN/CloudFront"]
        APIGateway["🚪 API Gateway"]
    end

    subgraph "Serverless Functions"
        Func1["⚡ Function 1"]
        Func2["⚡ Function 2"]
        Func3["⚡ Function 3"]
    end

    subgraph "Data & Storage"
        DDB["⚡ DynamoDB"]
        S3["☁️ S3"]
        FireDB["🔥 Firestore"]
    end

    subgraph "Event Driven"
        EventBus["📢 Event Bus"]
        SNS["📬 SNS/Pub-Sub"]
    end

    Web --> CDN
    CDN --> APIGateway
    APIGateway --> Func1
    APIGateway --> Func2
    
    Func1 --> DDB
    Func2 --> S3
    Func3 --> FireDB
    
    Func1 --> EventBus
    Func2 --> EventBus
    EventBus --> Func3
    
    Func3 --> SNS

    style Web fill:#e1f5ff
    style CDN fill:#fff3e0
    style APIGateway fill:#fff3e0
    style Func1 fill:#f3e5f5
    style Func2 fill:#f3e5f5
    style Func3 fill:#f3e5f5
    style DDB fill:#e8f5e9
    style S3 fill:#e8f5e9
    style FireDB fill:#e8f5e9
"""

    def _generate_hybrid_diagram(self) -> str:
        """Generate hybrid cloud architecture diagram."""
        return """graph TB
    subgraph "On-Premises"
        Legacy["🖥️ Legacy Systems"]
        OnPremDB["🗄️ On-Prem DB"]
    end

    subgraph "Hybrid Connection"
        VPN["🔒 VPN/Direct Connect"]
    end

    subgraph "Public Cloud - AWS"
        ALB["⚖️ Load Balancer"]
        subgraph "Kubernetes Cluster"
            Ingress["📥 Ingress"]
            Svc1["📦 Service 1"]
            Svc2["📦 Service 2"]
        end
    end

    subgraph "Cloud Managed Services"
        RDS["🗄️ Cloud DB"]
        S3["☁️ S3/Storage"]
        Cache["💾 ElastiCache"]
    end

    subgraph "Integration"
        Queue["📨 Message Queue"]
        API["🌐 API Hub"]
    end

    Legacy --> VPN
    OnPremDB --> VPN
    VPN --> ALB
    
    ALB --> Ingress
    Ingress --> Svc1
    Ingress --> Svc2
    
    Svc1 --> RDS
    Svc2 --> RDS
    Svc1 --> S3
    Svc2 --> S3
    Svc1 --> Cache
    
    Svc1 --> Queue
    Svc2 --> Queue
    
    Legacy --> API
    Svc1 --> API

    style Legacy fill:#ffebee
    style OnPremDB fill:#ffebee
    style Svc1 fill:#f3e5f5
    style Svc2 fill:#f3e5f5
    style RDS fill:#e8f5e9
    style S3 fill:#e8f5e9
    style Cache fill:#fce4ec
"""

    def generate_deployment_pipeline(self) -> str:
        """Generate CI/CD deployment pipeline diagram."""
        return """graph LR
    Developer["👨‍💻 Developer"]
    Git["📚 Git Repository"]
    CI["🔄 CI Pipeline"]
    Test["✅ Testing"]
    Build["🏗️ Build"]
    Registry["📦 Registry"]
    Staging["🔸 Staging"]
    Approval["👁️ Review"]
    Prod["🟢 Production"]

    Developer -->|Push Code| Git
    Git -->|Webhook| CI
    CI --> Test
    Test --> Build
    Build --> Registry
    Registry --> Staging
    Staging --> Approval
    Approval -->|Approved| Prod

    style Developer fill:#e1f5ff
    style Git fill:#fff3e0
    style CI fill:#f3e5f5
    style Test fill:#f3e5f5
    style Build fill:#f3e5f5
    style Staging fill:#fff3e0
    style Prod fill:#e8f5e9
"""

    def generate_k8s_deployment(self) -> str:
        """Generate Kubernetes deployment diagram."""
        return """graph TB
    subgraph "Kubernetes Cluster"
        subgraph "Ingress Layer"
            Ingress["📥 Ingress Controller"]
        end
        
        subgraph "Service Layer"
            Svc1["Service 1"]
            Svc2["Service 2"]
        end
        
        subgraph "Pod Layer"
            Pod1A["Pod 1A"]
            Pod1B["Pod 1B"]
            Pod1C["Pod 1C"]
            Pod2A["Pod 2A"]
            Pod2B["Pod 2B"]
        end
        
        subgraph "Storage"
            PVC1["PVC 1"]
            ConfigMap["ConfigMap"]
            Secret["Secret"]
        end
        
        subgraph "Monitoring"
            Metrics["📊 Metrics"]
            Logs["📝 Logs"]
        end
    end

    Ingress --> Svc1
    Ingress --> Svc2
    
    Svc1 --> Pod1A
    Svc1 --> Pod1B
    Svc1 --> Pod1C
    
    Svc2 --> Pod2A
    Svc2 --> Pod2B
    
    Pod1A --> PVC1
    Pod1B --> PVC1
    Pod1C --> ConfigMap
    Pod2A --> Secret
    Pod2B --> ConfigMap
    
    Pod1A --> Metrics
    Pod1B --> Metrics
    Pod2A --> Logs
    Pod2B --> Logs

    style Ingress fill:#fff3e0
    style Svc1 fill:#f3e5f5
    style Svc2 fill:#f3e5f5
    style Pod1A fill:#e1f5ff
    style Pod1B fill:#e1f5ff
    style Pod1C fill:#e1f5ff
    style Pod2A fill:#e1f5ff
    style Pod2B fill:#e1f5ff
    style PVC1 fill:#e8f5e9
    style Metrics fill:#fce4ec
    style Logs fill:#fce4ec
"""
