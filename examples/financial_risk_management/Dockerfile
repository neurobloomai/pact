# Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    postgresql-client \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Install application
RUN pip install -e .

# Create non-root user
RUN useradd --create-home --shell /bin/bash pact
RUN chown -R pact:pact /app
USER pact

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

EXPOSE 8000

CMD ["uvicorn", "pact_risk.main:app", "--host", "0.0.0.0", "--port", "8000"]

---
# docker-compose.yml
version: '3.8'

services:
  pact-risk-api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://postgres:password@postgres:5432/pact_risk
      - REDIS_URL=redis://redis:6379/0
      - ENVIRONMENT=development
    depends_on:
      - postgres
      - redis
    volumes:
      - ./logs:/app/logs
    restart: unless-stopped

  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: pact_risk
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./scripts/init_db.sql:/docker-entrypoint-initdb.d/init_db.sql
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    restart: unless-stopped

  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./monitoring/prometheus/prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.console.libraries=/etc/prometheus/console_libraries'
      - '--web.console.templates=/etc/prometheus/consoles'
    restart: unless-stopped

  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    volumes:
      - grafana_data:/var/lib/grafana
      - ./monitoring/grafana/dashboards:/etc/grafana/provisioning/dashboards
      - ./monitoring/grafana/datasources:/etc/grafana/provisioning/datasources
    restart: unless-stopped

volumes:
  postgres_data:
  redis_data:
  prometheus_data:
  grafana_data:

---
# kubernetes/namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: pact-risk
  labels:
    name: pact-risk

---
# kubernetes/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: pact-risk-api
  namespace: pact-risk
spec:
  replicas: 3
  selector:
    matchLabels:
      app: pact-risk-api
  template:
    metadata:
      labels:
        app: pact-risk-api
    spec:
      containers:
      - name: pact-risk-api
        image: neurobloom/pact-risk:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: pact-risk-secrets
              key: database-url
        - name: REDIS_URL
          value: "redis://redis-service:6379/0"
        - name: ENVIRONMENT
          value: "production"
        - name: SECRET_KEY
          valueFrom:
            secretKeyRef:
              name: pact-risk-secrets
              key: secret-key
        resources:
          requests:
            memory: "1Gi"
            cpu: "500m"
          limits:
            memory: "2Gi"
            cpu: "1000m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 60
          periodSeconds: 30
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 10
          periodSeconds: 5
        volumeMounts:
        - name: logs
          mountPath: /app/logs
      volumes:
      - name: logs
        emptyDir: {}

---
# kubernetes/service.yaml
apiVersion: v1
kind: Service
metadata:
  name: pact-risk-service
  namespace: pact-risk
spec:
  selector:
    app: pact-risk-api
  ports:
  - port: 8000
    targetPort: 8000
    protocol: TCP
  type: ClusterIP

---
# kubernetes/ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: pact-risk-ingress
  namespace: pact-risk
  annotations:
    kubernetes.io/ingress.class: nginx
    cert-manager.io/cluster-issuer: letsencrypt-prod
    nginx.ingress.kubernetes.io/rate-limit: "100"
spec:
  tls:
  - hosts:
    - api.pact-risk.neurobloom.ai
    secretName: pact-risk-tls
  rules:
  - host: api.pact-risk.neurobloom.ai
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: pact-risk-service
            port:
              number: 8000

---
# kubernetes/configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: pact-risk-config
  namespace: pact-risk
data:
  MONTE_CARLO_SIMULATIONS: "10000"
  VAR_CONFIDENCE_LEVELS: "0.95,0.99,0.999"
  PACT_MAX_RETRIES: "3"
  PACT_TIMEOUT_SECONDS: "30"
  LOG_LEVEL: "INFO"

---
# kubernetes/secrets.yaml (template)
apiVersion: v1
kind: Secret
metadata:
  name: pact-risk-secrets
  namespace: pact-risk
type: Opaque
data:
  database-url: <base64-encoded-database-url>
  secret-key: <base64-encoded-secret-key>
  market-data-api-key: <base64-encoded-api-key>

---
# monitoring/prometheus/prometheus.yml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  - "rules.yml"

scrape_configs:
  - job_name: 'pact-risk-api'
    static_configs:
      - targets: ['pact-risk-service:8000']
    metrics_path: '/metrics'
    scrape_interval: 10s

  - job_name: 'postgres'
    static_configs:
      - targets: ['postgres:5432']

  - job_name: 'redis'
    static_configs:
      - targets: ['redis:6379']

alerting:
  alertmanagers:
    - static_configs:
        - targets: ['alertmanager:9093']

---
# monitoring/prometheus/rules.yml
groups:
  - name: pact_risk_alerts
    rules:
    - alert: HighErrorRate
      expr: rate(pact_agent_errors_total[5m]) > 0.1
      for: 2m
      labels:
        severity: warning
      annotations:
        summary: "High error rate detected"
        description: "Agent {{ $labels.agent_id }} has error rate > 10%"

    - alert: HighLatency
      expr: histogram_quantile(0.95, rate(pact_agent_processing_seconds_bucket[5m])) > 1.0
      for: 2m
      labels:
        severity: warning
      annotations:
        summary: "High latency detected"
        description: "95th percentile latency > 1s for agent {{ $labels.agent_id }}"

    - alert: AgentDown
      expr: pact_agent_active == 0
      for: 1m
      labels:
        severity: critical
      annotations:
        summary: "Agent is down"
        description: "Agent {{ $labels.agent_id }} is not active"

    - alert: DatabaseConnectionFailure
      expr: up{job="postgres"} == 0
      for: 30s
      labels:
        severity: critical
      annotations:
        summary: "Database connection failure"
        description: "Cannot connect to PostgreSQL database"

    - alert: RedisConnectionFailure
      expr: up{job="redis"} == 0
      for: 30s
      labels:
        severity: critical
      annotations:
        summary: "Redis connection failure"
        description: "Cannot connect to Redis server"
