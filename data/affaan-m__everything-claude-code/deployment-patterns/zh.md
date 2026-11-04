---
name: deployment-patterns
description: 網頁應用程式的部署工作流程、CI/CD pipeline 模式、Docker 容器化、健康檢查、rollback 策略，以及 production 就緒檢查清單。當要設定 CI/CD、把應用程式容器化，或在 release 前檢查 production 就緒程度時使用。
metadata:
  origin: ECC
---

# 部署模式

Production 部署工作流程與 CI/CD 最佳實務。

## 何時啟用

- 設定 CI/CD pipeline
- 把應用程式 Docker 化
- 規劃部署策略（blue-green、canary、rolling）
- 實作健康檢查和 readiness probe
- 準備 production release
- 設定各環境專屬的設定

## 部署策略

### Rolling 部署（預設）

逐步替換實例，rollout 期間新舊版本會同時運行。

```
Instance 1: v1 → v2  (update first)
Instance 2: v1        (still running v1)
Instance 3: v1        (still running v1)

Instance 1: v2
Instance 2: v1 → v2  (update second)
Instance 3: v1

Instance 1: v2
Instance 2: v2
Instance 3: v1 → v2  (update last)
```

**優點：** 零停機、逐步 rollout
**缺點：** 兩個版本同時運行，所以變更必須向下相容
**適用時機：** 標準部署、向下相容的變更

### Blue-Green 部署

運行兩個一模一樣的環境。以原子方式切換流量。

```
Blue  (v1) ← traffic
Green (v2)   idle, running new version

# After verification:
Blue  (v1)   idle (becomes standby)
Green (v2) ← traffic
```

**優點：** 即時 rollback（切回 blue）、乾淨的切換
**缺點：** 部署期間需要 2 倍的基礎設施
**適用時機：** 關鍵服務、對問題零容忍

### Canary 部署

先把一小部分的流量導到新版本。

```
v1: 95% of traffic
v2:  5% of traffic  (canary)

# If metrics look good:
v1: 50% of traffic
v2: 50% of traffic

# Final:
v2: 100% of traffic
```

**優點：** 在全面 rollout 之前，用真實流量抓出問題
**缺點：** 需要流量分流的基礎設施和監控
**適用時機：** 高流量服務、有風險的變更、feature flag

## Docker

### Multi-Stage Dockerfile（Node.js）

```dockerfile
# Stage 1: Install dependencies
FROM node:22-alpine AS deps
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci --production=false

# Stage 2: Build
FROM node:22-alpine AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
RUN npm run build
RUN npm prune --production

# Stage 3: Production image
FROM node:22-alpine AS runner
WORKDIR /app

RUN addgroup -g 1001 -S appgroup && adduser -S appuser -u 1001
USER appuser

COPY --from=builder --chown=appuser:appgroup /app/node_modules ./node_modules
COPY --from=builder --chown=appuser:appgroup /app/dist ./dist
COPY --from=builder --chown=appuser:appgroup /app/package.json ./

ENV NODE_ENV=production
EXPOSE 3000

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD wget --no-verbose --tries=1 --spider http://localhost:3000/health || exit 1

CMD ["node", "dist/server.js"]
```

### Multi-Stage Dockerfile（Go）

```dockerfile
FROM golang:1.22-alpine AS builder
WORKDIR /app
COPY go.mod go.sum ./
RUN go mod download
COPY . .
RUN CGO_ENABLED=0 GOOS=linux go build -ldflags="-s -w" -o /server ./cmd/server

FROM alpine:3.19 AS runner
RUN apk --no-cache add ca-certificates
RUN adduser -D -u 1001 appuser
USER appuser

COPY --from=builder /server /server

EXPOSE 8080
HEALTHCHECK --interval=30s --timeout=3s CMD wget -qO- http://localhost:8080/health || exit 1
CMD ["/server"]
```

### Multi-Stage Dockerfile（Python/Django）

```dockerfile
FROM python:3.12-slim AS builder
WORKDIR /app
RUN pip install --no-cache-dir uv
COPY requirements.txt .
RUN uv pip install --system --no-cache -r requirements.txt

FROM python:3.12-slim AS runner
WORKDIR /app

RUN useradd -r -u 1001 appuser
USER appuser

COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin
COPY . .

ENV PYTHONUNBUFFERED=1
EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=3s CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health/')" || exit 1
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "4"]
```

### Docker 最佳實務

```
# GOOD practices
- Use specific version tags (node:22-alpine, not node:latest)
- Multi-stage builds to minimize image size
- Run as non-root user
- Copy dependency files first (layer caching)
- Use .dockerignore to exclude node_modules, .git, tests
- Add HEALTHCHECK instruction
- Set resource limits in docker-compose or k8s

# BAD practices
- Running as root
- Using :latest tags
- Copying entire repo in one COPY layer
- Installing dev dependencies in production image
- Storing secrets in image (use env vars or secrets manager)
```

## CI/CD Pipeline

### GitHub Actions（標準 Pipeline）

```yaml
name: CI/CD

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 22
          cache: npm
      - run: npm ci
      - run: npm run lint
      - run: npm run typecheck
      - run: npm test -- --coverage
      - uses: actions/upload-artifact@v4
        if: always()
        with:
          name: coverage
          path: coverage/

  build:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
      - uses: actions/checkout@v4
      - uses: docker/setup-buildx-action@v3
      - uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
      - uses: docker/build-push-action@v5
        with:
          push: true
          tags: ghcr.io/${{ github.repository }}:${{ github.sha }}
          cache-from: type=gha
          cache-to: type=gha,mode=max

  deploy:
    needs: build
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    environment: production
    steps:
      - name: Deploy to production
        run: |
          # Platform-specific deployment command
          # Railway: railway up
          # Vercel: vercel --prod
          # K8s: kubectl set image deployment/app app=ghcr.io/${{ github.repository }}:${{ github.sha }}
          echo "Deploying ${{ github.sha }}"
```

### Pipeline 階段

```
PR opened:
  lint → typecheck → unit tests → integration tests → preview deploy

Merged to main:
  lint → typecheck → unit tests → integration tests → build image → deploy staging → smoke tests → deploy production
```

## 健康檢查

### 健康檢查端點

```typescript
// Simple health check
app.get("/health", (req, res) => {
  res.status(200).json({ status: "ok" });
});

// Detailed health check (for internal monitoring)
app.get("/health/detailed", async (req, res) => {
  const checks = {
    database: await checkDatabase(),
    redis: await checkRedis(),
    externalApi: await checkExternalApi(),
  };

  const allHealthy = Object.values(checks).every(c => c.status === "ok");

  res.status(allHealthy ? 200 : 503).json({
    status: allHealthy ? "ok" : "degraded",
    timestamp: new Date().toISOString(),
    version: process.env.APP_VERSION || "unknown",
    uptime: process.uptime(),
    checks,
  });
});

async function checkDatabase(): Promise<HealthCheck> {
  try {
    await db.query("SELECT 1");
    return { status: "ok", latency_ms: 2 };
  } catch (err) {
    return { status: "error", message: "Database unreachable" };
  }
}
```

### Kubernetes Probe

```yaml
livenessProbe:
  httpGet:
    path: /health
    port: 3000
  initialDelaySeconds: 10
  periodSeconds: 30
  failureThreshold: 3

readinessProbe:
  httpGet:
    path: /health
    port: 3000
  initialDelaySeconds: 5
  periodSeconds: 10
  failureThreshold: 2

startupProbe:
  httpGet:
    path: /health
    port: 3000
  initialDelaySeconds: 0
  periodSeconds: 5
  failureThreshold: 30    # 30 * 5s = 150s max startup time
```

## 環境設定

### Twelve-Factor App 模式

```bash
# All config via environment variables — never in code
DATABASE_URL=postgres://user:pass@host:5432/db
REDIS_URL=redis://host:6379/0
API_KEY=${API_KEY}           # injected by secrets manager
LOG_LEVEL=info
PORT=3000

# Environment-specific behavior
NODE_ENV=production          # or staging, development
APP_ENV=production           # explicit app environment
```

### 設定驗證

```typescript
import { z } from "zod";

const envSchema = z.object({
  NODE_ENV: z.enum(["development", "staging", "production"]),
  PORT: z.coerce.number().default(3000),
  DATABASE_URL: z.string().url(),
  REDIS_URL: z.string().url(),
  JWT_SECRET: z.string().min(32),
  LOG_LEVEL: z.enum(["debug", "info", "warn", "error"]).default("info"),
});

// Validate at startup — fail fast if config is wrong
export const env = envSchema.parse(process.env);
```

## Rollback 策略

### 即時 Rollback

```bash
# Docker/Kubernetes: point to previous image
kubectl rollout undo deployment/app

# Vercel: promote previous deployment
vercel rollback

# Railway: redeploy previous commit
railway up --commit <previous-sha>

# Database: rollback migration (if reversible)
npx prisma migrate resolve --rolled-back <migration-name>
```

### Rollback 檢查清單

- [ ] 前一個 image/artifact 可用而且有打 tag
- [ ] 資料庫 migration 向下相容（沒有破壞性的變更）
- [ ] feature flag 可以在不 deploy 的情況下停用新功能
- [ ] 已設定錯誤率飆升的監控警報
- [ ] production release 之前，已在 staging 測試過 rollback

## Production 就緒檢查清單

任何 production 部署之前：

### 應用程式
- [ ] 所有測試通過（單元、整合、E2E）
- [ ] 程式碼或設定檔裡沒有寫死的 secret
- [ ] 錯誤處理涵蓋所有邊界情況
- [ ] log 是結構化的（JSON），而且不含個資
- [ ] 健康檢查端點回傳有意義的狀態

### 基礎設施
- [ ] Docker image 可以重現地 build（版本已固定）
- [ ] 環境變數有文件記錄，並且在啟動時驗證
- [ ] 已設定資源限制（CPU、記憶體）
- [ ] 已設定水平擴展（最小/最大實例數）
- [ ] 所有端點都啟用 SSL/TLS

### 監控
- [ ] 已匯出應用程式指標（請求速率、延遲、錯誤）
- [ ] 已設定錯誤率超過門檻的警報
- [ ] 已設定 log 彙整（結構化 log、可搜尋）
- [ ] 對健康檢查端點做 uptime 監控

### 安全
- [ ] 已掃描相依套件的 CVE
- [ ] CORS 只設定允許的來源
- [ ] 公開端點已啟用 rate limiting
- [ ] 已驗證認證與授權
- [ ] 已設定安全標頭（CSP、HSTS、X-Frame-Options）

### 營運
- [ ] rollback 計畫已記錄並測試過
- [ ] 資料庫 migration 已用 production 規模的資料測試過
- [ ] 有常見失敗情境的 runbook
- [ ] 已定義 on-call 輪值和升級路徑
