---
name: istio-traffic-management
description: 設定 Istio 流量管理，包含路由、負載平衡、circuit breaker 與 canary deploy。適用於實作 service mesh 的流量政策、漸進式交付或 resilience 模式的時候。
---

# Istio 流量管理

為 production 的 service mesh deploy 提供 Istio 流量管理的完整指南。

## 什麼時候用這個 Skill

- 設定服務之間的路由
- 實作 canary 或 blue-green deploy
- 設定 circuit breaker 與重試
- 負載平衡設定
- 為測試做流量鏡像
- 為 chaos engineering 做 fault injection

## 核心概念

### 1. 流量管理資源

| 資源                | 用途                          | 範圍          |
| ------------------- | ----------------------------- | ------------- |
| **VirtualService**  | 把流量路由到目的地            | 以 host 為基礎 |
| **DestinationRule** | 定義路由之後的政策            | 以服務為基礎  |
| **Gateway**         | 設定 ingress/egress           | Cluster 邊緣  |
| **ServiceEntry**    | 加入外部服務                  | 整個 mesh     |

### 2. 流量走向

```
Client → Gateway → VirtualService → DestinationRule → Service
                   （路由）        （政策）          （pod）
```

## 範本

### 範本 1：基本路由

```yaml
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: reviews-route
  namespace: bookinfo
spec:
  hosts:
    - reviews
  http:
    - match:
        - headers:
            end-user:
              exact: jason
      route:
        - destination:
            host: reviews
            subset: v2
    - route:
        - destination:
            host: reviews
            subset: v1
---
apiVersion: networking.istio.io/v1beta1
kind: DestinationRule
metadata:
  name: reviews-destination
  namespace: bookinfo
spec:
  host: reviews
  subsets:
    - name: v1
      labels:
        version: v1
    - name: v2
      labels:
        version: v2
    - name: v3
      labels:
        version: v3
```

### 範本 2：Canary Deploy

```yaml
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: my-service-canary
spec:
  hosts:
    - my-service
  http:
    - route:
        - destination:
            host: my-service
            subset: stable
          weight: 90
        - destination:
            host: my-service
            subset: canary
          weight: 10
---
apiVersion: networking.istio.io/v1beta1
kind: DestinationRule
metadata:
  name: my-service-dr
spec:
  host: my-service
  trafficPolicy:
    connectionPool:
      tcp:
        maxConnections: 100
      http:
        h2UpgradePolicy: UPGRADE
        http1MaxPendingRequests: 100
        http2MaxRequests: 1000
  subsets:
    - name: stable
      labels:
        version: stable
    - name: canary
      labels:
        version: canary
```

### 範本 3：Circuit Breaker

```yaml
apiVersion: networking.istio.io/v1beta1
kind: DestinationRule
metadata:
  name: circuit-breaker
spec:
  host: my-service
  trafficPolicy:
    connectionPool:
      tcp:
        maxConnections: 100
      http:
        http1MaxPendingRequests: 100
        http2MaxRequests: 1000
        maxRequestsPerConnection: 10
        maxRetries: 3
    outlierDetection:
      consecutive5xxErrors: 5
      interval: 30s
      baseEjectionTime: 30s
      maxEjectionPercent: 50
      minHealthPercent: 30
```

### 範本 4：重試與 Timeout

```yaml
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: ratings-retry
spec:
  hosts:
    - ratings
  http:
    - route:
        - destination:
            host: ratings
      timeout: 10s
      retries:
        attempts: 3
        perTryTimeout: 3s
        retryOn: connect-failure,refused-stream,unavailable,cancelled,retriable-4xx,503
        retryRemoteLocalities: true
```

### 範本 5：流量鏡像

```yaml
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: mirror-traffic
spec:
  hosts:
    - my-service
  http:
    - route:
        - destination:
            host: my-service
            subset: v1
      mirror:
        host: my-service
        subset: v2
      mirrorPercentage:
        value: 100.0
```

### 範本 6：Fault Injection

```yaml
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: fault-injection
spec:
  hosts:
    - ratings
  http:
    - fault:
        delay:
          percentage:
            value: 10
          fixedDelay: 5s
        abort:
          percentage:
            value: 5
          httpStatus: 503
      route:
        - destination:
            host: ratings
```

### 範本 7：Ingress Gateway

```yaml
apiVersion: networking.istio.io/v1beta1
kind: Gateway
metadata:
  name: my-gateway
spec:
  selector:
    istio: ingressgateway
  servers:
    - port:
        number: 443
        name: https
        protocol: HTTPS
      tls:
        mode: SIMPLE
        credentialName: my-tls-secret
      hosts:
        - "*.example.com"
---
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: my-vs
spec:
  hosts:
    - "api.example.com"
  gateways:
    - my-gateway
  http:
    - match:
        - uri:
            prefix: /api/v1
      route:
        - destination:
            host: api-service
            port:
              number: 8080
```

## 負載平衡策略

```yaml
apiVersion: networking.istio.io/v1beta1
kind: DestinationRule
metadata:
  name: load-balancing
spec:
  host: my-service
  trafficPolicy:
    loadBalancer:
      simple: ROUND_ROBIN # 或 LEAST_CONN、RANDOM、PASSTHROUGH
---
# 以 consistent hashing 做 sticky session
apiVersion: networking.istio.io/v1beta1
kind: DestinationRule
metadata:
  name: sticky-sessions
spec:
  host: my-service
  trafficPolicy:
    loadBalancer:
      consistentHash:
        httpHeaderName: x-user-id
        # 或：httpCookie、useSourceIp、httpQueryParameterName
```

## 最佳實務

### 該做的

- **從簡單開始**：逐步增加複雜度
- **使用 subset**：清楚地為你的服務標示版本
- **設定 timeout**：一定要設定合理的 timeout
- **啟用重試**：但要搭配 backoff 和上限
- **監控**：用 Kiali 和 Jaeger 取得可見度

### 不該做的

- **不要過度重試**：可能造成連鎖失敗
- **不要忽略 outlier detection**：啟用 circuit breaker
- **不要鏡像到 production**：要鏡像到測試環境
- **不要跳過 canary**：先用一小部分流量測試

## 除錯指令

```bash
# 檢查 VirtualService 設定
istioctl analyze

# 檢視生效的路由
istioctl proxy-config routes deploy/my-app -o json

# 檢查 endpoint 探索
istioctl proxy-config endpoints deploy/my-app

# 除錯流量
istioctl proxy-config log deploy/my-app --level debug
```
