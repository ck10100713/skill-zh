---
name: github-actions-templates
description: 為測試、建置與 deploy 應用程式提供可上 production 的 GitHub Actions workflow 範本。適用於為專案建立 CI/CD、自動化測試與 deploy 流程，或設定安全的 GitHub Actions workflow 的時候。
---

# GitHub Actions 範本

可上 production 的 GitHub Actions workflow 模式，用於測試、建置和 deploy 應用程式。

## 目的

為各種技術棧建立有效率又安全的 GitHub Actions workflow，用於持續整合與部署。

## 什麼時候用

- 自動化測試與 deploy
- 建置 Docker image 並 push 到 registry
- Deploy 到 Kubernetes cluster
- 執行安全掃描
- 為多個環境實作 matrix build

## 常見的 Workflow 模式

### 模式 1：測試 Workflow

```yaml
name: Test

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest

    strategy:
      matrix:
        node-version: [18.x, 20.x]

    steps:
      - uses: actions/checkout@v4

      - name: Use Node.js ${{ matrix.node-version }}
        uses: actions/setup-node@v4
        with:
          node-version: ${{ matrix.node-version }}
          cache: "npm"

      - name: Install dependencies
        run: npm ci

      - name: Run linter
        run: npm run lint

      - name: Run tests
        run: npm test

      - name: Upload coverage
        uses: codecov/codecov-action@v4
        with:
          files: ./coverage/lcov.info
```

### 模式 2：建置並推送 Docker Image

```yaml
name: Build and Push

on:
  push:
    branches: [main]
    tags: ["v*"]

env:
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}

jobs:
  build:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write

    steps:
      - uses: actions/checkout@v4

      - name: Log in to Container Registry
        uses: docker/login-action@v3
        with:
          registry: ${{ env.REGISTRY }}
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: Extract metadata
        id: meta
        uses: docker/metadata-action@v5
        with:
          images: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}
          tags: |
            type=ref,event=branch
            type=ref,event=pr
            type=semver,pattern={{version}}
            type=semver,pattern={{major}}.{{minor}}

      - name: Build and push
        uses: docker/build-push-action@v5
        with:
          context: .
          push: true
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}
          cache-from: type=gha
          cache-to: type=gha,mode=max
```

### 模式 3：Deploy 到 Kubernetes

```yaml
name: Deploy to Kubernetes

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v4
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: us-west-2

      - name: Update kubeconfig
        run: |
          aws eks update-kubeconfig --name production-cluster --region us-west-2

      - name: Deploy to Kubernetes
        run: |
          kubectl apply -f k8s/
          kubectl rollout status deployment/my-app -n production
          kubectl get services -n production

      - name: Verify deployment
        run: |
          kubectl get pods -n production
          kubectl describe deployment my-app -n production
```

### 模式 4：Matrix Build

```yaml
name: Matrix Build

on: [push, pull_request]

jobs:
  build:
    runs-on: ${{ matrix.os }}

    strategy:
      matrix:
        os: [ubuntu-latest, macos-latest, windows-latest]
        python-version: ["3.9", "3.10", "3.11", "3.12"]

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt

      - name: Run tests
        run: pytest
```

## Workflow 最佳實務

1. **使用特定的 action 版本**（@v4，不要用 @latest）
2. **快取相依套件**以加快建置
3. **使用 secret** 處理敏感資料
4. **在 PR 上實作狀態檢查**
5. **使用 matrix build** 做多版本測試
6. **設定適當的權限**
7. **常見模式使用 reusable workflow**
8. **為 production 實作審核關卡**
9. **為失敗加上通知步驟**
10. **敏感的工作負載使用 self-hosted runner**

## Reusable Workflow

```yaml
# .github/workflows/reusable-test.yml
name: Reusable Test Workflow

on:
  workflow_call:
    inputs:
      node-version:
        required: true
        type: string
    secrets:
      NPM_TOKEN:
        required: true

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: ${{ inputs.node-version }}
      - run: npm ci
      - run: npm test
```

**使用 reusable workflow：**

```yaml
jobs:
  call-test:
    uses: ./.github/workflows/reusable-test.yml
    with:
      node-version: "20.x"
    secrets:
      NPM_TOKEN: ${{ secrets.NPM_TOKEN }}
```

## 安全掃描

```yaml
name: Security Scan

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  security:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: Run Trivy vulnerability scanner
        uses: aquasecurity/trivy-action@0.28.0
        with:
          scan-type: "fs"
          scan-ref: "."
          format: "sarif"
          output: "trivy-results.sarif"

      - name: Upload Trivy results to GitHub Security
        uses: github/codeql-action/upload-sarif@v3
        with:
          sarif_file: "trivy-results.sarif"

      - name: Run Snyk Security Scan
        uses: snyk/actions/node@0.4.0
        env:
          SNYK_TOKEN: ${{ secrets.SNYK_TOKEN }}
```

## 搭配審核的 Deploy

```yaml
name: Deploy to Production

on:
  push:
    tags: ["v*"]

jobs:
  deploy:
    runs-on: ubuntu-latest
    environment:
      name: production
      url: https://app.example.com

    steps:
      - uses: actions/checkout@v4

      - name: Deploy application
        run: |
          echo "Deploying to production..."
          # 在這裡放 deploy 指令

      - name: Notify Slack
        if: success()
        uses: slackapi/slack-github-action@v1
        with:
          webhook-url: ${{ secrets.SLACK_WEBHOOK }}
          payload: |
            {
              "text": "Deployment to production completed successfully!"
            }
```


## 相關 Skill

- `gitlab-ci-patterns`：GitLab CI workflow
- `deployment-pipeline-design`：pipeline 架構
- `secrets-management`：secret 處理
