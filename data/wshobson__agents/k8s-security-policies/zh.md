---
name: k8s-security-policies
description: 實作 Kubernetes 安全政策，包含 NetworkPolicy、PodSecurityPolicy 與 RBAC，達到正式環境等級的安全性。在加固 Kubernetes cluster、實作網路隔離或落實 pod 安全標準時使用。
---

# Kubernetes Security Policies

在 Kubernetes 實作 NetworkPolicy、PodSecurityPolicy、RBAC 與 Pod Security Standards 的完整指南。

## Purpose

用 network policy、pod security standards 和 RBAC，替 Kubernetes cluster 做縱深防禦。

## When to Use This Skill

- 實作網路分段
- 設定 pod security standards
- 建立符合最小權限的 RBAC
- 為合規需求建立安全政策
- 實作 admission control
- 加固多租戶 cluster

## Pod Security Standards

### 1. Privileged (Unrestricted)

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: privileged-ns
  labels:
    pod-security.kubernetes.io/enforce: privileged
    pod-security.kubernetes.io/audit: privileged
    pod-security.kubernetes.io/warn: privileged
```

### 2. Baseline (Minimally restrictive)

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: baseline-ns
  labels:
    pod-security.kubernetes.io/enforce: baseline
    pod-security.kubernetes.io/audit: baseline
    pod-security.kubernetes.io/warn: baseline
```

### 3. Restricted (Most restrictive)

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: restricted-ns
  labels:
    pod-security.kubernetes.io/enforce: restricted
    pod-security.kubernetes.io/audit: restricted
    pod-security.kubernetes.io/warn: restricted
```

## Network Policies

### Default Deny All

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: default-deny-all
  namespace: production
spec:
  podSelector: {}
  policyTypes:
    - Ingress
    - Egress
```

### Allow Frontend to Backend

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-frontend-to-backend
  namespace: production
spec:
  podSelector:
    matchLabels:
      app: backend
  policyTypes:
    - Ingress
  ingress:
    - from:
        - podSelector:
            matchLabels:
              app: frontend
      ports:
        - protocol: TCP
          port: 8080
```

### Allow DNS

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-dns
  namespace: production
spec:
  podSelector: {}
  policyTypes:
    - Egress
  egress:
    - to:
        - namespaceSelector:
            matchLabels:
              name: kube-system
      ports:
        - protocol: UDP
          port: 53
```

**參考：** 見 `assets/network-policy-template.yaml`

## RBAC Configuration

### Role (Namespace-scoped)

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: pod-reader
  namespace: production
rules:
  - apiGroups: [""]
    resources: ["pods"]
    verbs: ["get", "watch", "list"]
```

### ClusterRole (Cluster-wide)

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: secret-reader
rules:
  - apiGroups: [""]
    resources: ["secrets"]
    verbs: ["get", "watch", "list"]
```

### RoleBinding

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: read-pods
  namespace: production
subjects:
  - kind: User
    name: jane
    apiGroup: rbac.authorization.k8s.io
  - kind: ServiceAccount
    name: default
    namespace: production
roleRef:
  kind: Role
  name: pod-reader
  apiGroup: rbac.authorization.k8s.io
```

**參考：** 見 `references/rbac-patterns.md`

## Pod Security Context

### Restricted Pod

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: secure-pod
spec:
  securityContext:
    runAsNonRoot: true
    runAsUser: 1000
    fsGroup: 1000
    seccompProfile:
      type: RuntimeDefault
  containers:
    - name: app
      image: myapp:1.0
      securityContext:
        allowPrivilegeEscalation: false
        readOnlyRootFilesystem: true
        capabilities:
          drop:
            - ALL
```

## Policy Enforcement with OPA Gatekeeper

### ConstraintTemplate

```yaml
apiVersion: templates.gatekeeper.sh/v1
kind: ConstraintTemplate
metadata:
  name: k8srequiredlabels
spec:
  crd:
    spec:
      names:
        kind: K8sRequiredLabels
      validation:
        openAPIV3Schema:
          type: object
          properties:
            labels:
              type: array
              items:
                type: string
  targets:
    - target: admission.k8s.gatekeeper.sh
      rego: |
        package k8srequiredlabels
        violation[{"msg": msg, "details": {"missing_labels": missing}}] {
          provided := {label | input.review.object.metadata.labels[label]}
          required := {label | label := input.parameters.labels[_]}
          missing := required - provided
          count(missing) > 0
          msg := sprintf("missing required labels: %v", [missing])
        }
```

### Constraint

```yaml
apiVersion: constraints.gatekeeper.sh/v1beta1
kind: K8sRequiredLabels
metadata:
  name: require-app-label
spec:
  match:
    kinds:
      - apiGroups: ["apps"]
        kinds: ["Deployment"]
  parameters:
    labels: ["app", "environment"]
```

## Service Mesh Security (Istio)

### PeerAuthentication (mTLS)

```yaml
apiVersion: security.istio.io/v1beta1
kind: PeerAuthentication
metadata:
  name: default
  namespace: production
spec:
  mtls:
    mode: STRICT
```

### AuthorizationPolicy

```yaml
apiVersion: security.istio.io/v1beta1
kind: AuthorizationPolicy
metadata:
  name: allow-frontend
  namespace: production
spec:
  selector:
    matchLabels:
      app: backend
  action: ALLOW
  rules:
    - from:
        - source:
            principals: ["cluster.local/ns/production/sa/frontend"]
```

## Best Practices

1. **在 namespace 層級實作 Pod Security Standards**
2. **用 Network Policies** 做網路分段
3. **對所有 service account 套用最小權限的 RBAC**
4. **啟用 admission control**（OPA Gatekeeper/Kyverno）
5. **用非 root 身分跑 container**
6. **使用唯讀的 root filesystem**
7. **除非必要，否則 drop 所有 capabilities**
8. **實作 resource quota** 和 limit range
9. **對安全事件啟用 audit logging**
10. **定期對 image 做安全掃描**

## Compliance Frameworks

### CIS Kubernetes Benchmark

- 使用 RBAC 授權
- 啟用 audit logging
- 使用 Pod Security Standards
- 設定 network policy
- 實作 secrets 靜態加密
- 啟用 node 身分驗證

### NIST Cybersecurity Framework

- 實作縱深防禦
- 使用網路分段
- 設定安全監控
- 實作存取控制
- 啟用 logging 與監控

## Troubleshooting

**NetworkPolicy 沒作用：**

```bash
# Check if CNI supports NetworkPolicy
kubectl get nodes -o wide
kubectl describe networkpolicy <name>
```

**RBAC 權限被拒：**

```bash
# Check effective permissions
kubectl auth can-i list pods --as system:serviceaccount:default:my-sa
kubectl auth can-i '*' '*' --as system:serviceaccount:default:my-sa
```


## Related Skills

- `k8s-manifest-generator` - 用來建立安全的 manifest
- `gitops-workflow` - 用來自動部署政策
