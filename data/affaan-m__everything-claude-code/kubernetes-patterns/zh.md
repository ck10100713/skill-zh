---
name: kubernetes-patterns
description: 可上 production 的 Kubernetes workload 模式、資源管理、RBAC、probe、autoscaling、ConfigMap/Secret 處理，以及 kubectl 除錯。在撰寫或 review Kubernetes manifest，或除錯 probe、RBAC、autoscaling、resource limit 時使用。
metadata:
  origin: ECC
---

# Kubernetes Patterns

用來可靠地部署、管理與除錯 workload 的 production 等級 Kubernetes 模式。

## 何時啟用

- 撰寫 Kubernetes manifest（Deployment、Service、Ingress、Job）
- 設定 resource requests/limits、liveness/readiness probe
- 設定 RBAC、namespace 或 ServiceAccount
- 在 K8s 中管理設定與 secret
- 除錯 CrashLoopBackOff、OOMKilled、pending pod 或 image pull 錯誤
- 設定 HPA（Horizontal Pod Autoscaler）或 PodDisruptionBudget
- Review K8s YAML 的安全性或正確性

## 何時使用

> 同上面的「何時啟用」。這個別名是為了符合 repo 的 skill 格式慣例。只要你在撰寫、review 或除錯 Kubernetes YAML 與 workload，就用這個 skill。

## 運作方式

這個 skill 提供**可直接複製貼上、production 等級的 YAML 模式**與 **kubectl 除錯指令**，依任務整理如下：

1. **Deployment 範本**：完整設定好的 production `Deployment`，包含 security context、rolling update 策略、三種 probe、resource limit，以及從 ConfigMap/Secret 注入環境變數。
2. **Probe**：startup、liveness、readiness 的選用決策表，附上正確的 `failureThreshold × periodSeconds` 算法。
3. **Service 與 Ingress**：ClusterIP、LoadBalancer，以及搭配 cert-manager annotation 的 TLS Ingress 模式。
4. **ConfigMap 與 Secret**：`envFrom`、掛載成檔案，以及外部 secret 的做法。
5. **資源管理**：依 workload 類型（web API、JVM、worker、sidecar）整理 requests 與 limits 的經驗法則。
6. **RBAC**：最小權限的 ServiceAccount → Role → RoleBinding 鏈。
7. **HPA 與 PDB**：autoscaling 與節點 drain 安全性的設定。
8. **Job 與 CronJob**：一次性與排程 workload 的模式，搭配正確的 `restartPolicy`。
9. **kubectl 速查表**：logs、exec、rollback、port-forward、dry-run，以及常見錯誤的診斷指令。
10. **反模式與檢查清單**：哪些事不要做，以及安全／可靠度／可觀測性檢查清單。

## 範例

完整、可執行的範例見下面各節。快速索引：

| 任務 | 跳到 |
|------|---------|
| 完整的 production Deployment YAML | [Core Workload Patterns](#core-workload-patterns) |
| Probe 設定 | [Probes](#probes--liveness-readiness-startup) |
| RBAC 最小權限設定 | [RBAC](#rbac--roles-and-serviceaccounts) |
| 除錯 CrashLoopBackOff | [kubectl Debugging Cheatsheet](#kubectl-debugging-cheatsheet) |
| Autoscaling | [HPA](#horizontal-pod-autoscaler-hpa) |

---

## Core Workload Patterns

### Deployment：Production 範本

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: my-app
  namespace: my-namespace
  labels:
    app: my-app
    version: "1.0.0"
spec:
  replicas: 3
  selector:
    matchLabels:
      app: my-app
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1          # Allow 1 extra pod during update
      maxUnavailable: 0    # Never reduce below desired count
  template:
    metadata:
      labels:
        app: my-app
        version: "1.0.0"
    spec:
      # Security context at pod level
      securityContext:
        runAsNonRoot: true
        runAsUser: 1001
        fsGroup: 1001

      # Graceful shutdown
      terminationGracePeriodSeconds: 30

      containers:
        - name: my-app
          image: ghcr.io/org/my-app:1.0.0   # Never use :latest
          imagePullPolicy: IfNotPresent

          ports:
            - containerPort: 8080
              protocol: TCP

          # Resource requests AND limits are both required
          resources:
            requests:
              cpu: "100m"
              memory: "128Mi"
            limits:
              cpu: "500m"
              memory: "256Mi"

          # Container security context
          securityContext:
            allowPrivilegeEscalation: false
            readOnlyRootFilesystem: true
            capabilities:
              drop:
                - ALL

          # Probes (see Probes section below)
          startupProbe:
            httpGet:
              path: /health
              port: 8080
            failureThreshold: 30
            periodSeconds: 5
          livenessProbe:
            httpGet:
              path: /health
              port: 8080
            initialDelaySeconds: 0
            periodSeconds: 30
            failureThreshold: 3
          readinessProbe:
            httpGet:
              path: /ready
              port: 8080
            initialDelaySeconds: 5
            periodSeconds: 10
            failureThreshold: 2

          # Environment from ConfigMap and Secret
          envFrom:
            - configMapRef:
                name: my-app-config
          env:
            - name: DB_PASSWORD
              valueFrom:
                secretKeyRef:
                  name: my-app-secrets
                  key: db-password

          # Writable tmp directory when readOnlyRootFilesystem: true
          volumeMounts:
            - name: tmp
              mountPath: /tmp

      volumes:
        - name: tmp
          emptyDir: {}
```

---

## Probes — Liveness, Readiness, Startup

要用哪一種 probe、什麼時候用，一定要搞清楚：

| Probe | 失敗時的動作 | 適用情境 |
|-------|---------------|---------|
| `startupProbe` | 啟動太慢就砍掉 container | 啟動很慢的 app（JVM、Python） |
| `livenessProbe` | 重啟 container | 偵測 deadlock／卡死的 process |
| `readinessProbe` | 從 Service endpoint 移除 | 暫時無法服務（例如 DB 重新連線） |

```yaml
# Correct pattern: startupProbe covers slow startup,
# then liveness/readiness take over
startupProbe:
  httpGet:
    path: /health
    port: 8080
  failureThreshold: 30  # 30 * 5s = 150s max startup time
  periodSeconds: 5

livenessProbe:
  httpGet:
    path: /health
    port: 8080
  periodSeconds: 30
  failureThreshold: 3   # 3 * 30s = 90s before restart

readinessProbe:
  httpGet:
    path: /ready         # Separate endpoint: checks DB, cache, etc.
    port: 8080
  periodSeconds: 10
  failureThreshold: 2
```

```yaml
# WRONG: initialDelaySeconds without startupProbe
# If the app takes 60s to start, set a startupProbe instead
livenessProbe:
  httpGet:
    path: /health
    port: 8080
  initialDelaySeconds: 60   # BAD: Arbitrary wait, race condition
```

---

## Service 與 Ingress

### Service 類型

```yaml
# ClusterIP (default) — internal-only
apiVersion: v1
kind: Service
metadata:
  name: my-app
  namespace: my-namespace
spec:
  selector:
    app: my-app
  ports:
    - port: 80
      targetPort: 8080
      protocol: TCP
  type: ClusterIP
```

```yaml
# LoadBalancer — external traffic (cloud providers)
spec:
  type: LoadBalancer
  ports:
    - port: 443
      targetPort: 8080
```

### 搭配 TLS 的 Ingress

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: my-app
  namespace: my-namespace
  annotations:
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
spec:
  ingressClassName: nginx
  tls:
    - hosts:
        - myapp.example.com
      secretName: my-app-tls
  rules:
    - host: myapp.example.com
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: my-app
                port:
                  number: 80
```

---

## ConfigMap 與 Secret

### ConfigMap：非敏感設定

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: my-app-config
  namespace: my-namespace
data:
  LOG_LEVEL: "info"
  APP_ENV: "production"
  MAX_CONNECTIONS: "100"
  # Mount as a file for complex config
  app.yaml: |
    server:
      port: 8080
      timeout: 30s
```

```yaml
# Mount ConfigMap as a file
volumes:
  - name: config
    configMap:
      name: my-app-config
      items:
        - key: app.yaml
          path: app.yaml
volumeMounts:
  - name: config
    mountPath: /etc/app
    readOnly: true
```

### Secret：敏感資料

```bash
# Create secret from literal (CLI, then store in Vault/SOPS)
kubectl create secret generic my-app-secrets \
  --from-literal=db-password='s3cr3t' \
  --namespace=my-namespace \
  --dry-run=client -o yaml | kubectl apply -f -
```

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: my-app-secrets
  namespace: my-namespace
type: Opaque
# Values are base64-encoded (NOT encrypted — use Sealed Secrets or ESO for real encryption)
data:
  db-password: czNjcjN0  # base64 of 's3cr3t'
```

> **重要：**原生的 Kubernetes Secret 只是 base64 編碼，除非 cluster 有設定加密，否則 at rest 時並沒有加密。production 請用 [Sealed Secrets](https://github.com/bitnami-labs/sealed-secrets) 或 [External Secrets Operator](https://external-secrets.io)。

---

## Resource Requests 與 Limits

```yaml
resources:
  requests:       # Scheduler uses this to place the pod
    cpu: "100m"   # 100 millicores = 0.1 CPU
    memory: "128Mi"
  limits:         # Container is killed/throttled above this
    cpu: "500m"
    memory: "256Mi"
```

**經驗法則：**

| Workload 類型 | CPU Request | Memory Request | 備註 |
|---------------|-------------|----------------|-------|
| Web API | 100–250m | 128–256Mi | limit 設成 request 的 2–4 倍 |
| Worker/consumer | 250–500m | 256–512Mi | memory limit 設成等於 request，行為比較可預期 |
| JVM app | 500m–1 | 512Mi–2Gi | `-Xmx` 之上要留空間給 JVM 本身的開銷 |
| Sidecar | 10–50m | 32–64Mi | 保持最小 |

```yaml
# WRONG: No requests or limits — unpredictable scheduling, OOM evictions
containers:
  - name: app
    image: myapp:latest
    # Missing resources: {} — this is dangerous in production

# WRONG: Limits without requests — requests default to limits, over-reserves capacity
resources:
  limits:
    cpu: "2"
    memory: "1Gi"
  # requests missing — will default to limits values
```

---

## RBAC — Roles and ServiceAccounts

### 最小權限原則

**依 app 是否會呼叫 Kubernetes API，有兩種模式：**

#### 模式 A：App 不需要 Kubernetes API（大多數 app）

關掉 ServiceAccount 的 token 自動掛載。不需要 Role/RoleBinding。

```yaml
# ServiceAccount with token disabled — safest default
apiVersion: v1
kind: ServiceAccount
metadata:
  name: my-app-sa
  namespace: my-namespace
automountServiceAccountToken: false   # No K8s API token injected into pods
```

```yaml
# Reference in Deployment — no token, no API access
spec:
  template:
    spec:
      serviceAccountName: my-app-sa
      automountServiceAccountToken: false   # Belt-and-suspenders: also set at pod level
```

#### 模式 B：App 需要 Kubernetes API（operator、controller、config watcher）

啟用 token，只授予實際需要的權限。

```yaml
# 1. ServiceAccount — enable token for this SA
apiVersion: v1
kind: ServiceAccount
metadata:
  name: my-app-sa
  namespace: my-namespace
automountServiceAccountToken: true    # Token required: app calls K8s API
```

```yaml
# 2. Role — grant only what the app needs (namespace-scoped)
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: my-app-role
  namespace: my-namespace
rules:
  - apiGroups: [""]
    resources: ["configmaps"]
    verbs: ["get", "list", "watch"]    # Read-only, specific resource
  - apiGroups: [""]
    resources: ["secrets"]
    resourceNames: ["my-app-secrets"]  # Restrict to specific secret by name
    verbs: ["get"]
```

```yaml
# 3. Bind Role to ServiceAccount
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: my-app-rolebinding
  namespace: my-namespace
subjects:
  - kind: ServiceAccount
    name: my-app-sa
    namespace: my-namespace
roleRef:
  kind: Role
  apiGroup: rbac.authorization.k8s.io
  name: my-app-role
```

```yaml
# 4. Reference SA in Deployment
spec:
  template:
    spec:
      serviceAccountName: my-app-sa
      # automountServiceAccountToken defaults to true from SA — token is injected
```

---

## Horizontal Pod Autoscaler (HPA)

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: my-app-hpa
  namespace: my-namespace
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: my-app
  minReplicas: 2      # Always at least 2 for HA
  maxReplicas: 10
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 70    # Scale up when avg CPU > 70%
    - type: Resource
      resource:
        name: memory
        target:
          type: Utilization
          averageUtilization: 80
```

> HPA 需要所有 container 都設定 `resources.requests`，因為它是用 `current / request` 來計算使用率。

---

## PodDisruptionBudget (PDB)

避免在節點 drain 或 rolling update 時，同時有太多 pod 被關掉：

```yaml
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: my-app-pdb
  namespace: my-namespace
spec:
  minAvailable: 2           # OR use maxUnavailable: 1
  selector:
    matchLabels:
      app: my-app
```

---

## Namespace 與多租戶

```bash
# Create namespace with resource quotas
kubectl create namespace my-namespace

# Apply ResourceQuota to limit namespace consumption
kubectl apply -f - <<EOF
apiVersion: v1
kind: ResourceQuota
metadata:
  name: my-namespace-quota
  namespace: my-namespace
spec:
  hard:
    requests.cpu: "4"
    requests.memory: 4Gi
    limits.cpu: "8"
    limits.memory: 8Gi
    pods: "20"
EOF
```

---

## Job 與 CronJob

```yaml
# One-off Job (DB migration, data processing)
apiVersion: batch/v1
kind: Job
metadata:
  name: db-migrate
  namespace: my-namespace
spec:
  backoffLimit: 3          # Retry up to 3 times on failure
  ttlSecondsAfterFinished: 3600   # Auto-delete after 1h
  template:
    spec:
      restartPolicy: OnFailure    # Never for Jobs (not Always)
      containers:
        - name: migrate
          image: ghcr.io/org/my-app:1.0.0
          command: ["python", "manage.py", "migrate"]
          resources:
            requests:
              cpu: "100m"
              memory: "256Mi"
```

```yaml
# CronJob
apiVersion: batch/v1
kind: CronJob
metadata:
  name: cleanup-job
  namespace: my-namespace
spec:
  schedule: "0 2 * * *"         # 2am daily
  concurrencyPolicy: Forbid      # Don't run if previous still running
  successfulJobsHistoryLimit: 3
  failedJobsHistoryLimit: 1
  jobTemplate:
    spec:
      template:
        spec:
          restartPolicy: OnFailure
          containers:
            - name: cleanup
              image: ghcr.io/org/cleanup:1.0.0
              resources:
                requests:
                  cpu: "50m"
                  memory: "64Mi"
```

---

## kubectl Debugging Cheatsheet

```bash
# --- Pod status and logs ---
kubectl get pods -n my-namespace
kubectl get pods -n my-namespace -o wide          # Show node assignment
kubectl describe pod <pod-name> -n my-namespace   # Events and state details
kubectl logs <pod-name> -n my-namespace           # Current logs
kubectl logs <pod-name> -n my-namespace --previous  # Logs from crashed container
kubectl logs <pod-name> -n my-namespace -c <container>  # Multi-container pod

# --- Execute into a running container ---
kubectl exec -it <pod-name> -n my-namespace -- sh
kubectl exec -it <pod-name> -n my-namespace -- bash

# --- Check resource usage ---
kubectl top pods -n my-namespace
kubectl top nodes

# --- Deployment operations ---
kubectl rollout status deployment/my-app -n my-namespace
kubectl rollout history deployment/my-app -n my-namespace
kubectl rollout undo deployment/my-app -n my-namespace      # Rollback
kubectl rollout undo deployment/my-app --to-revision=2 -n my-namespace

# --- Scale manually ---
kubectl scale deployment my-app --replicas=5 -n my-namespace

# --- Inspect events (cluster-wide issues) ---
kubectl get events -n my-namespace --sort-by='.lastTimestamp'

# --- Port-forward for local debugging ---
kubectl port-forward pod/<pod-name> 8080:8080 -n my-namespace
kubectl port-forward svc/my-app 8080:80 -n my-namespace

# --- Dry-run to validate YAML ---
kubectl apply -f deployment.yaml --dry-run=client
kubectl apply -f deployment.yaml --dry-run=server   # Validates against live cluster
```

### 診斷常見錯誤

```bash
# CrashLoopBackOff: container keeps crashing
kubectl logs <pod-name> --previous -n my-namespace  # Check crash logs
kubectl describe pod <pod-name> -n my-namespace     # Check exit code & OOMKilled

# ImagePullBackOff: can't pull image
kubectl describe pod <pod-name> -n my-namespace     # Check Events section
# Causes: wrong image tag, missing imagePullSecret, private registry

# Pending pod: not scheduled
kubectl describe pod <pod-name> -n my-namespace
# Causes: insufficient resources, no matching node selector, taint/toleration mismatch

# OOMKilled: out of memory
# Increase memory limits, check for memory leaks
kubectl describe pod <pod-name> -n my-namespace | grep -A5 "Last State"
```

---

## 反模式

```yaml
# BAD: Using :latest tag — non-deterministic deployments
image: myapp:latest

# GOOD: Pin to a specific immutable tag (SHA or semver)
image: ghcr.io/org/myapp:1.4.2
# or
image: ghcr.io/org/myapp@sha256:abc123...

# ---

# BAD: Running as root
securityContext: {}    # Defaults to root

# GOOD: Non-root with explicit UID
securityContext:
  runAsNonRoot: true
  runAsUser: 1001

# ---

# BAD: No resource limits — one pod can starve the entire node
containers:
  - name: app
    image: myapp:1.0.0
    # No resources defined

# GOOD: Always set requests and limits
resources:
  requests:
    cpu: "100m"
    memory: "128Mi"
  limits:
    cpu: "500m"
    memory: "256Mi"

# ---

# BAD: Storing plaintext secrets in ConfigMaps
apiVersion: v1
kind: ConfigMap
data:
  DB_PASSWORD: "mysecretpassword"   # NEVER — use Secret or external secrets manager

# ---

# BAD: ClusterAdmin for application service accounts
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
roleRef:
  kind: ClusterRole
  name: cluster-admin    # Grants god-mode to your app

# ---

# BAD: minAvailable: 0 in PDB — defeats the purpose
spec:
  minAvailable: 0

# ---

# BAD: restartPolicy: Always in a Job (causes infinite restart loop)
spec:
  restartPolicy: Always   # Use OnFailure or Never for Jobs
```

---

## 最佳實務檢查清單

### 安全
- [ ] Container 以非 root 身分執行（設定 `runAsNonRoot: true`、`runAsUser`）
- [ ] 設定 `readOnlyRootFilesystem: true`，需要寫入的路徑用 `emptyDir`
- [ ] `allowPrivilegeEscalation: false`
- [ ] 移除所有 capability（`capabilities.drop: [ALL]`）
- [ ] 每個 app 使用專屬的 ServiceAccount，不要用 `default`
- [ ] 除非需要，否則 `automountServiceAccountToken: false`
- [ ] RBAC 遵循最小權限（用 `Role`，除非必要不要用 `ClusterRole`）
- [ ] Secret 透過 Sealed Secrets 或 External Secrets Operator 管理

### 可靠度
- [ ] 三種 probe 都設定好（startup + liveness + readiness）
- [ ] 每個 container 都設定 resource requests 與 limits
- [ ] 任何 production workload 都要 `minReplicas: 2+`
- [ ] stateful 或關鍵服務要定義 PodDisruptionBudget
- [ ] `RollingUpdate` 策略搭配 `maxUnavailable: 0`
- [ ] 負載會變動的服務要設定 HPA

### 可觀測性
- [ ] App 提供 `/health`（liveness）與 `/ready`（readiness）endpoint
- [ ] 結構化 JSON log（log 裡不可有 PII）
- [ ] Resource label：`app`、`version`、`environment`

---

## 相關 Skill

- `docker-patterns`：multi-stage Dockerfile 與 image 安全
- `deployment-patterns`：CI/CD pipeline、rollback 策略、health check endpoint
- `security-review`：更廣的安全強化脈絡
- `git-workflow`：與 K8s 整合的 GitOps（ArgoCD / Flux 模式）
