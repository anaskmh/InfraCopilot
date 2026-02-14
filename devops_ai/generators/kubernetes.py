"""Kubernetes YAML generator."""

from typing import List

from .base import BaseGenerator


class KubernetesGenerator(BaseGenerator):
    """Generate Kubernetes manifests."""

    def generate(self, requirements: str) -> str:
        """Generate Kubernetes YAML from requirements."""
        if not self.validate_input(requirements):
            return "# Error: Invalid requirements"

        requirements_lower = requirements.lower()
        manifests = []

        # Generate Namespace
        manifests.append(self._generate_namespace())

        # Add monitoring stack (Prometheus + Grafana) if requested
        if any(x in requirements_lower for x in ["monitoring", "prometheus", "grafana"]):
            manifests.append(self._generate_monitoring_namespace())
            manifests.append(self._generate_prometheus_rbac())
            manifests.append(self._generate_prometheus_configmap())
            manifests.append(self._generate_prometheus_deployment())
            manifests.append(self._generate_prometheus_service())
            manifests.append(self._generate_grafana_configmap())
            manifests.append(self._generate_grafana_deployment())
            manifests.append(self._generate_grafana_service())

        # Add logging stack if requested
        if any(x in requirements_lower for x in ["logging", "logs", "loki", "elk"]):
            manifests.append(self._generate_logging_namespace())
            manifests.append(self._generate_fluent_bit_rbac())
            manifests.append(self._generate_fluent_bit_configmap())
            manifests.append(self._generate_fluent_bit_daemonset())

        # Add security policies if requested
        if any(x in requirements_lower for x in ["security", "rbac", "policy", "secure"]):
            manifests.append(self._generate_rbac_policies())
            manifests.append(self._generate_network_policies())
            manifests.append(self._generate_pod_security_policies())

        # Detect and generate application components
        if any(x in requirements_lower for x in ["deployment", "deploy", "app", "service"]):
            manifests.append(self._generate_deployment())
            manifests.append(self._generate_service())

        if any(x in requirements_lower for x in ["database", "db", "stateful"]):
            manifests.append(self._generate_statefulset())

        if any(x in requirements_lower for x in ["ingress"]):
            manifests.append(self._generate_ingress())

        if any(x in requirements_lower for x in ["configmap", "config"]):
            manifests.append(self._generate_configmap())

        if any(x in requirements_lower for x in ["secret"]):
            manifests.append(self._generate_secret())

        if any(x in requirements_lower for x in ["hpa", "autoscal"]):
            manifests.append(self._generate_hpa())

        # Join manifests with separator
        return "\n---\n".join(manifests)

    def _generate_namespace(self) -> str:
        """Generate namespace."""
        return f"""apiVersion: v1
kind: Namespace
metadata:
  name: {self.project_name}
  labels:
    name: {self.project_name}"""

    def _generate_deployment(self) -> str:
        """Generate deployment."""
        return f"""apiVersion: apps/v1
kind: Deployment
metadata:
  name: {self.project_name}-deployment
  namespace: {self.project_name}
  labels:
    app: {self.project_name}
spec:
  replicas: 3
  selector:
    matchLabels:
      app: {self.project_name}
  template:
    metadata:
      labels:
        app: {self.project_name}
    spec:
      containers:
      - name: {self.project_name}-container
        image: {self.project_name}:latest
        ports:
        - containerPort: 8080
        env:
        - name: ENVIRONMENT
          value: production
        resources:
          requests:
            cpu: 100m
            memory: 128Mi
          limits:
            cpu: 500m
            memory: 512Mi
        livenessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8080
          initialDelaySeconds: 5
          periodSeconds: 5"""

    def _generate_service(self) -> str:
        """Generate service."""
        return f"""apiVersion: v1
kind: Service
metadata:
  name: {self.project_name}-service
  namespace: {self.project_name}
  labels:
    app: {self.project_name}
spec:
  type: LoadBalancer
  selector:
    app: {self.project_name}
  ports:
  - name: http
    port: 80
    targetPort: 8080
    protocol: TCP"""

    def _generate_statefulset(self) -> str:
        """Generate stateful set for databases."""
        return f"""apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: {self.project_name}-db
  namespace: {self.project_name}
spec:
  serviceName: {self.project_name}-db-headless
  replicas: 1
  selector:
    matchLabels:
      app: {self.project_name}-db
  template:
    metadata:
      labels:
        app: {self.project_name}-db
    spec:
      containers:
      - name: postgres
        image: postgres:15-alpine
        ports:
        - containerPort: 5432
        env:
        - name: POSTGRES_DB
          valueFrom:
            configMapKeyRef:
              name: {self.project_name}-config
              key: db_name
        - name: POSTGRES_USER
          valueFrom:
            secretKeyRef:
              name: {self.project_name}-secret
              key: db_user
        - name: POSTGRES_PASSWORD
          valueFrom:
            secretKeyRef:
              name: {self.project_name}-secret
              key: db_password
        volumeMounts:
        - name: data
          mountPath: /var/lib/postgresql/data
  volumeClaimTemplates:
  - metadata:
      name: data
    spec:
      accessModes: [ "ReadWriteOnce" ]
      resources:
        requests:
          storage: 10Gi"""

    def _generate_ingress(self) -> str:
        """Generate ingress."""
        return f"""apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: {self.project_name}-ingress
  namespace: {self.project_name}
  annotations:
    cert-manager.io/cluster-issuer: letsencrypt-prod
spec:
  ingressClassName: nginx
  tls:
  - hosts:
    - {self.project_name}.example.com
    secretName: {self.project_name}-tls
  rules:
  - host: {self.project_name}.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: {self.project_name}-service
            port:
              number: 80"""

    def _generate_configmap(self) -> str:
        """Generate ConfigMap."""
        return f"""apiVersion: v1
kind: ConfigMap
metadata:
  name: {self.project_name}-config
  namespace: {self.project_name}
data:
  db_name: "{self.project_name}_db"
  log_level: "INFO"
  cache_ttl: "3600"
  api_timeout: "30"
  max_connections: "100\""""

    def _generate_secret(self) -> str:
        """Generate secret template."""
        return f"""apiVersion: v1
kind: Secret
metadata:
  name: {self.project_name}-secret
  namespace: {self.project_name}
type: Opaque
data:
  db_user: YWRtaW4=  # base64 encoded 'admin'
  db_password: Y2hhbmdlbWU=  # base64 encoded 'changeme' - CHANGE THIS!
  api_key: Y2hhbmdlbWU=  # base64 encoded 'changeme' - CHANGE THIS!"""

    def _generate_hpa(self) -> str:
        """Generate Horizontal Pod Autoscaler."""
        return f"""apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: {self.project_name}-hpa
  namespace: {self.project_name}
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: {self.project_name}-deployment
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80"""

    def _generate_monitoring_namespace(self) -> str:
        """Generate monitoring namespace for Prometheus and Grafana."""
        return f"""apiVersion: v1
kind: Namespace
metadata:
  name: monitoring
  labels:
    name: monitoring"""

    def _generate_prometheus_rbac(self) -> str:
        """Generate RBAC for Prometheus with least privilege."""
        return f"""# Prometheus RBAC
apiVersion: v1
kind: ServiceAccount
metadata:
  name: prometheus
  namespace: monitoring

---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: prometheus
rules:
- apiGroups: [""]
  resources:
  - nodes
  - nodes/proxy
  - services
  - endpoints
  - pods
  verbs: ["get", "list", "watch"]
- apiGroups:
  - extensions
  resources:
  - ingresses
  verbs: ["get", "list", "watch"]
- nonResourceURLs: ["/metrics"]
  verbs: ["get"]

---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: prometheus
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: ClusterRole
  name: prometheus
subjects:
- kind: ServiceAccount
  name: prometheus
  namespace: monitoring"""

    def _generate_prometheus_configmap(self) -> str:
        """Generate Prometheus configuration."""
        return f"""apiVersion: v1
kind: ConfigMap
metadata:
  name: prometheus-config
  namespace: monitoring
data:
  prometheus.yml: |
    global:
      scrape_interval: 15s
      evaluation_interval: 15s
      external_labels:
        cluster: {self.project_name}

    scrape_configs:
    - job_name: 'kubernetes-apiservers'
      kubernetes_sd_configs:
      - role: endpoints
      scheme: https
      tls_config:
        ca_file: /var/run/secrets/kubernetes.io/serviceaccount/ca.crt
      bearer_token_file: /var/run/secrets/kubernetes.io/serviceaccount/token
      relabel_configs:
      - source_labels: [__meta_kubernetes_namespace, __meta_kubernetes_service_name, __meta_kubernetes_endpoint_port_name]
        action: keep
        regex: default;kubernetes;https

    - job_name: 'kubernetes-nodes'
      kubernetes_sd_configs:
      - role: node
      scheme: https
      tls_config:
        ca_file: /var/run/secrets/kubernetes.io/serviceaccount/ca.crt
      bearer_token_file: /var/run/secrets/kubernetes.io/serviceaccount/token
      relabel_configs:
      - action: labelmap
        regex: __meta_kubernetes_node_label_(.+)
      - target_label: __address__
        replacement: kubernetes.default.svc:443
      - source_labels: [__meta_kubernetes_node_name]
        regex: (.+)
        target_label: __metrics_path__
        replacement: /api/v1/nodes/${{1}}/proxy/metrics

    - job_name: 'kubernetes-pods'
      kubernetes_sd_configs:
      - role: pod
      relabel_configs:
      - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_scrape]
        action: keep
        regex: 'true'
      - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_path]
        action: replace
        target_label: __metrics_path__
        regex: (.+)
      - source_labels: [__address__, __meta_kubernetes_pod_annotation_prometheus_io_port]
        action: replace
        regex: ([^:]+)(?::\\d+)?;(\\d+)
        replacement: $1:$2
        target_label: __address__
      - action: labelmap
        regex: __meta_kubernetes_pod_label_(.+)
      - source_labels: [__meta_kubernetes_namespace]
        action: replace
        target_label: kubernetes_namespace
      - source_labels: [__meta_kubernetes_pod_name]
        action: replace
        target_label: kubernetes_pod_name"""

    def _generate_prometheus_deployment(self) -> str:
        """Generate Prometheus deployment."""
        return f"""apiVersion: apps/v1
kind: Deployment
metadata:
  name: prometheus
  namespace: monitoring
  labels:
    app: prometheus
spec:
  replicas: 2
  selector:
    matchLabels:
      app: prometheus
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
  template:
    metadata:
      labels:
        app: prometheus
      annotations:
        prometheus.io/scrape: "true"
        prometheus.io/port: "9090"
    spec:
      serviceAccountName: prometheus
      securityContext:
        runAsNonRoot: true
        runAsUser: 65534
        fsGroup: 65534
      containers:
      - name: prometheus
        image: prom/prometheus:latest
        args:
          - '--config.file=/etc/prometheus/prometheus.yml'
          - '--storage.tsdb.path=/prometheus'
          - '--storage.tsdb.retention.time=30d'
        ports:
        - name: web
          containerPort: 9090
        resources:
          requests:
            cpu: 500m
            memory: 512Mi
          limits:
            cpu: 1000m
            memory: 1Gi
        livenessProbe:
          httpGet:
            path: /-/healthy
            port: 9090
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /-/ready
            port: 9090
          initialDelaySeconds: 5
          periodSeconds: 5
        volumeMounts:
        - name: config
          mountPath: /etc/prometheus
        - name: storage
          mountPath: /prometheus
        securityContext:
          allowPrivilegeEscalation: false
          readOnlyRootFilesystem: true
          runAsNonRoot: true
          capabilities:
            drop:
            - ALL
      volumes:
      - name: config
        configMap:
          name: prometheus-config
      - name: storage
        emptyDir: {{}}
      affinity:
        podAntiAffinity:
          preferredDuringSchedulingIgnoredDuringExecution:
          - weight: 100
            podAffinityTerm:
              labelSelector:
                matchExpressions:
                - key: app
                  operator: In
                  values:
                  - prometheus
              topologyKey: kubernetes.io/hostname"""

    def _generate_prometheus_service(self) -> str:
        """Generate Prometheus service."""
        return f"""apiVersion: v1
kind: Service
metadata:
  name: prometheus
  namespace: monitoring
  labels:
    app: prometheus
spec:
  type: ClusterIP
  ports:
  - name: web
    port: 9090
    targetPort: 9090
  selector:
    app: prometheus"""

    def _generate_grafana_configmap(self) -> str:
        """Generate Grafana configuration."""
        return f"""apiVersion: v1
kind: ConfigMap
metadata:
  name: grafana-config
  namespace: monitoring
data:
  grafana.ini: |
    [security]
    admin_user = admin
    admin_password = changeme
    [auth.anonymous]
    enabled = false
    [users]
    allow_sign_up = false

---
apiVersion: v1
kind: ConfigMap
metadata:
  name: grafana-datasources
  namespace: monitoring
data:
  prometheus.yaml: |
    apiVersion: 1
    datasources:
    - name: Prometheus
      type: prometheus
      url: http://prometheus:9090
      access: proxy
      isDefault: true"""

    def _generate_grafana_deployment(self) -> str:
        """Generate Grafana deployment."""
        return f"""apiVersion: apps/v1
kind: Deployment
metadata:
  name: grafana
  namespace: monitoring
  labels:
    app: grafana
spec:
  replicas: 1
  selector:
    matchLabels:
      app: grafana
  template:
    metadata:
      labels:
        app: grafana
    spec:
      securityContext:
        runAsNonRoot: true
        runAsUser: 472
        fsGroup: 472
      containers:
      - name: grafana
        image: grafana/grafana:latest
        env:
        - name: GF_SECURITY_ADMIN_PASSWORD
          valueFrom:
            secretKeyRef:
              name: grafana-secret
              key: admin-password
        ports:
        - containerPort: 3000
          name: web
        resources:
          requests:
            cpu: 100m
            memory: 128Mi
          limits:
            cpu: 500m
            memory: 512Mi
        volumeMounts:
        - name: storage
          mountPath: /var/lib/grafana
        - name: config
          mountPath: /etc/grafana
        - name: datasources
          mountPath: /etc/grafana/provisioning/datasources
        securityContext:
          allowPrivilegeEscalation: false
          readOnlyRootFilesystem: true
          runAsNonRoot: true
          capabilities:
            drop:
            - ALL
      volumes:
      - name: storage
        emptyDir: {{}}
      - name: config
        configMap:
          name: grafana-config
      - name: datasources
        configMap:
          name: grafana-datasources

---
apiVersion: v1
kind: Secret
metadata:
  name: grafana-secret
  namespace: monitoring
type: Opaque
stringData:
  admin-password: "changeme"  # CHANGE THIS!"""

    def _generate_grafana_service(self) -> str:
        """Generate Grafana service."""
        return f"""apiVersion: v1
kind: Service
metadata:
  name: grafana
  namespace: monitoring
  labels:
    app: grafana
spec:
  type: LoadBalancer
  ports:
  - port: 3000
    targetPort: 3000
  selector:
    app: grafana"""

    def _generate_logging_namespace(self) -> str:
        """Generate logging namespace."""
        return f"""apiVersion: v1
kind: Namespace
metadata:
  name: logging
  labels:
    name: logging"""

    def _generate_fluent_bit_rbac(self) -> str:
        """Generate RBAC for Fluent Bit."""
        return f"""apiVersion: v1
kind: ServiceAccount
metadata:
  name: fluent-bit
  namespace: logging

---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: fluent-bit
rules:
- apiGroups: [""]
  resources:
  - pods
  - namespaces
  verbs: ["get", "list", "watch"]

---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: fluent-bit
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: ClusterRole
  name: fluent-bit
subjects:
- kind: ServiceAccount
  name: fluent-bit
  namespace: logging"""

    def _generate_fluent_bit_configmap(self) -> str:
        """Generate Fluent Bit configuration."""
        return f"""apiVersion: v1
kind: ConfigMap
metadata:
  name: fluent-bit-config
  namespace: logging
data:
  fluent-bit.conf: |
    [SERVICE]
        Flush         5
        Daemon        Off
        Log_Level     info
        Parsers_File  parsers.conf

    [INPUT]
        Name              tail
        Path              /var/log/containers/*.log
        Parser            docker
        Tag               kube.*
        Refresh_Interval  5
        Mem_Buf_Limit     5MB
        Skip_Long_Lines   On

    [INPUT]
        Name            systemd
        Tag             host.*
        Systemd_Filter  _SYSTEMD_UNIT=kubelet.service
        Read_From_Tail  On

    [FILTER]
        Name                kubernetes
        Match               kube.*
        Kube_URL            https://kubernetes.default.svc:443
        Kube_CA_File        /var/run/secrets/kubernetes.io/serviceaccount/ca.crt
        Kube_Token_File     /var/run/secrets/kubernetes.io/serviceaccount/token
        Kube_Tag_Prefix     kube.var.log.containers.
        Merge_Log           On
        Keep_Log            Off
        K8S-Logging.Parser  On
        K8S-Logging.Exclude On

    [OUTPUT]
        Name   stdout
        Match  *

  parsers.conf: |
    [PARSER]
        Name   docker
        Format json
        Time_Key time
        Time_Format %Y-%m-%dT%H:%M:%S.%L%z"""

    def _generate_fluent_bit_daemonset(self) -> str:
        """Generate Fluent Bit DaemonSet for logging."""
        return f"""apiVersion: apps/v1
kind: DaemonSet
metadata:
  name: fluent-bit
  namespace: logging
  labels:
    app: fluent-bit
spec:
  selector:
    matchLabels:
      app: fluent-bit
  template:
    metadata:
      labels:
        app: fluent-bit
    spec:
      serviceAccountName: fluent-bit
      securityContext:
        runAsNonRoot: true
        runAsUser: 1000
      tolerations:
      - key: node-role.kubernetes.io/master
        operator: Exists
        effect: NoSchedule
      containers:
      - name: fluent-bit
        image: fluent/fluent-bit:latest
        env:
        - name: FLUENT_ELASTICSEARCH_HOST
          value: "elasticsearch"
        - name: FLUENT_ELASTICSEARCH_PORT
          value: "9200"
        resources:
          requests:
            cpu: 100m
            memory: 128Mi
          limits:
            cpu: 200m
            memory: 256Mi
        volumeMounts:
        - name: varlog
          mountPath: /var/log
        - name: varlibdockercontainers
          mountPath: /var/lib/docker/containers
          readOnly: true
        - name: config
          mountPath: /fluent-bit/etc/
        securityContext:
          allowPrivilegeEscalation: false
          readOnlyRootFilesystem: true
          capabilities:
            drop:
            - ALL
      volumes:
      - name: varlog
        hostPath:
          path: /var/log
      - name: varlibdockercontainers
        hostPath:
          path: /var/lib/docker/containers
      - name: config
        configMap:
          name: fluent-bit-config"""

    def _generate_rbac_policies(self) -> str:
        """Generate RBAC policies with least privilege."""
        return f"""# RBAC policies with least privilege

apiVersion: v1
kind: ServiceAccount
metadata:
  name: {self.project_name}-sa
  namespace: {self.project_name}

---
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: {self.project_name}-role
  namespace: {self.project_name}
rules:
- apiGroups: [""]
  resources: ["configmaps"]
  verbs: ["get", "list", "watch"]
- apiGroups: [""]
  resources: ["secrets"]
  verbs: ["get"]
- apiGroups: ["apps"]
  resources: ["deployments", "statefulsets"]
  verbs: ["get", "list"]

---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: {self.project_name}-rolebinding
  namespace: {self.project_name}
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: Role
  name: {self.project_name}-role
subjects:
- kind: ServiceAccount
  name: {self.project_name}-sa
  namespace: {self.project_name}"""

    def _generate_network_policies(self) -> str:
        """Generate NetworkPolicies for pod communication."""
        return f"""# NetworkPolicies - deny-all ingress, then allow specific traffic

apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: {self.project_name}-deny-all
  namespace: {self.project_name}
spec:
  podSelector: {{}}
  policyTypes:
  - Ingress

---
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: {self.project_name}-allow-internal
  namespace: {self.project_name}
spec:
  podSelector:
    matchLabels:
      app: {self.project_name}
  policyTypes:
  - Ingress
  ingress:
  - from:
    - podSelector:
        matchLabels:
          app: {self.project_name}
    ports:
    - protocol: TCP
      port: 8080

---
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-dns
  namespace: {self.project_name}
spec:
  podSelector: {{}}
  policyTypes:
  - Egress
  egress:
  - to:
    - namespaceSelector:
        matchLabels:
          name: kube-system
    ports:
    - protocol: UDP
      port: 53"""

    def _generate_pod_security_policies(self) -> str:
        """Generate Pod Security policies and SecurityContext best practices."""
        return f"""# Pod Security Context best practices

apiVersion: v1
kind: Pod
metadata:
  name: {self.project_name}-security-example
  namespace: {self.project_name}
spec:
  securityContext:
    runAsNonRoot: true
    runAsUser: 1000
    fsGroup: 2000
    seccompProfile:
      type: RuntimeDefault
  containers:
  - name: app
    image: {self.project_name}:latest
    securityContext:
      allowPrivilegeEscalation: false
      readOnlyRootFilesystem: true
      runAsNonRoot: true
      runAsUser: 1000
      capabilities:
        drop:
        - ALL
        add:
        - NET_BIND_SERVICE
    volumeMounts:
    - name: tmp
      mountPath: /tmp
  volumes:
  - name: tmp
    emptyDir: {{}}"""
