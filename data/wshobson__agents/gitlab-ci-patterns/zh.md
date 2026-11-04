---
name: gitlab-ci-patterns
description: 建構具備多階段流程、快取與分散式 runner 的 GitLab CI/CD pipeline，用於可擴充的自動化。適用於實作 GitLab CI/CD、最佳化 pipeline 效能，或設定自動化測試與 deploy 的時候。
---

# GitLab CI 模式

完整的 GitLab CI/CD pipeline 模式，用於自動化測試、建置與 deploy。

## 目的

建立有效率的 GitLab CI pipeline，具備適當的階段劃分、快取與 deploy 策略。

## 什麼時候用

- 自動化以 GitLab 為基礎的 CI/CD
- 實作多階段 pipeline
- 設定 GitLab Runner
- 從 GitLab deploy 到 Kubernetes
- 實作 GitOps 工作流程

## 基本 Pipeline 結構

```yaml
stages:
  - build
  - test
  - deploy

variables:
  DOCKER_DRIVER: overlay2
  DOCKER_TLS_CERTDIR: "/certs"

build:
  stage: build
  image: node:20
  script:
    - npm ci
    - npm run build
  artifacts:
    paths:
      - dist/
    expire_in: 1 hour
  cache:
    key: ${CI_COMMIT_REF_SLUG}
    paths:
      - node_modules/

test:
  stage: test
  image: node:20
  script:
    - npm ci
    - npm run lint
    - npm test
  coverage: '/Lines\s*:\s*(\d+\.\d+)%/'
  artifacts:
    reports:
      coverage_report:
        coverage_format: cobertura
        path: coverage/cobertura-coverage.xml

deploy:
  stage: deploy
  image: bitnami/kubectl:1.31
  script:
    - kubectl apply -f k8s/
    - kubectl rollout status deployment/my-app
  only:
    - main
  environment:
    name: production
    url: https://app.example.com
```

## Docker 建置與推送

```yaml
build-docker:
  stage: build
  image: docker:24
  services:
    - docker:24-dind
  before_script:
    - docker login -u $CI_REGISTRY_USER -p $CI_REGISTRY_PASSWORD $CI_REGISTRY
  script:
    - docker build -t $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA .
    - docker build -t $CI_REGISTRY_IMAGE:latest .
    - docker push $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA
    - docker push $CI_REGISTRY_IMAGE:latest
  only:
    - main
    - tags
```

## 多環境 Deploy

把 `KUBE_CA_CERT_FILE` 設為 GitLab 的 file variable，內容是 cluster 的 CA 憑證，
並透過受保護且遮罩的 CI variable 提供 `KUBE_TOKEN`。這個 file variable
的內容是一個路徑，kubectl 用它來驗證 API server 的憑證。要同時保護
`develop` 和 `main`，這樣 deploy job 才能讀取受保護的 token。

```yaml
.deploy_template: &deploy_template
  image: bitnami/kubectl:1.31
  before_script:
    - kubectl config set-cluster k8s --server="$KUBE_URL" --certificate-authority="$KUBE_CA_CERT_FILE" --embed-certs=true
    - kubectl config set-credentials admin --token="$KUBE_TOKEN"
    - kubectl config set-context default --cluster=k8s --user=admin
    - kubectl config use-context default

deploy:staging:
  <<: *deploy_template
  stage: deploy
  script:
    - kubectl apply -f k8s/ -n staging
    - kubectl rollout status deployment/my-app -n staging
  environment:
    name: staging
    url: https://staging.example.com
  only:
    - develop

deploy:production:
  <<: *deploy_template
  stage: deploy
  script:
    - kubectl apply -f k8s/ -n production
    - kubectl rollout status deployment/my-app -n production
  environment:
    name: production
    url: https://app.example.com
  when: manual
  only:
    - main
```

## Terraform Pipeline

```yaml
stages:
  - validate
  - plan
  - apply

variables:
  TF_ROOT: ${CI_PROJECT_DIR}/terraform
  TF_VERSION: "1.6.0"

before_script:
  - cd ${TF_ROOT}
  - terraform --version

validate:
  stage: validate
  image: hashicorp/terraform:${TF_VERSION}
  script:
    - terraform init -backend=false
    - terraform validate
    - terraform fmt -check

plan:
  stage: plan
  image: hashicorp/terraform:${TF_VERSION}
  script:
    - terraform init
    - terraform plan -out=tfplan
  artifacts:
    paths:
      - ${TF_ROOT}/tfplan
    expire_in: 1 day

apply:
  stage: apply
  image: hashicorp/terraform:${TF_VERSION}
  script:
    - terraform init
    - terraform apply -auto-approve tfplan
  dependencies:
    - plan
  when: manual
  only:
    - main
```

## 安全掃描

```yaml
include:
  - template: Security/SAST.gitlab-ci.yml
  - template: Security/Dependency-Scanning.gitlab-ci.yml
  - template: Security/Container-Scanning.gitlab-ci.yml

trivy-scan:
  stage: test
  image: aquasec/trivy:0.58.0
  script:
    - trivy image --exit-code 1 --severity HIGH,CRITICAL $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA
  allow_failure: true
```

## 快取策略

```yaml
# 快取 node_modules
build:
  cache:
    key: ${CI_COMMIT_REF_SLUG}
    paths:
      - node_modules/
    policy: pull-push

# 全域快取
cache:
  key: ${CI_COMMIT_REF_SLUG}
  paths:
    - .cache/
    - vendor/

# 每個 job 各自的快取
job1:
  cache:
    key: job1-cache
    paths:
      - build/

job2:
  cache:
    key: job2-cache
    paths:
      - dist/
```

## 動態 Child Pipeline

```yaml
generate-pipeline:
  stage: build
  script:
    - python generate_pipeline.py > child-pipeline.yml
  artifacts:
    paths:
      - child-pipeline.yml

trigger-child:
  stage: deploy
  trigger:
    include:
      - artifact: child-pipeline.yml
        job: generate-pipeline
    strategy: depend
```


## 最佳實務

1. **使用特定的 image tag**（node:20，不要用 node:latest）
2. **適當地快取**相依套件
3. **使用 artifact** 存放建置輸出
4. **為 production 實作手動關卡**
5. **使用 environment** 追蹤 deploy
6. **啟用 merge request pipeline**
7. **使用 pipeline schedule** 處理週期性的 job
8. **實作安全掃描**
9. **使用 CI/CD variable** 處理 secret
10. **監控 pipeline 效能**

## 相關 Skill

- `github-actions-templates`：GitHub Actions
- `deployment-pipeline-design`：架構
- `secrets-management`：secret 處理
