---
name: secrets-management
description: 用 Vault、AWS Secrets Manager 或各平台原生方案，為 CI/CD pipeline 實作安全的 secrets 管理。在處理敏感憑證、輪替 secret 或保護 CI/CD 環境時使用。
---

# Secrets Management

用 Vault、AWS Secrets Manager 和其他工具，為 CI/CD pipeline 做安全的 secrets 管理實務。

## Purpose

在 CI/CD pipeline 裡實作安全的 secrets 管理，不要把敏感資訊寫死在程式碼裡。

## When to Use

- 儲存 API key 和憑證
- 管理資料庫密碼
- 處理 TLS 憑證
- 自動輪替 secret
- 實作最小權限存取

## Secrets Management Tools

### HashiCorp Vault

- 集中式 secrets 管理
- 動態產生 secret
- Secret 輪替
- 稽核 logging
- 細粒度的存取控制

### AWS Secrets Manager

- AWS 原生方案
- 自動輪替
- 與 RDS 整合
- 支援 CloudFormation

### Azure Key Vault

- Azure 原生方案
- 由 HSM 支撐的金鑰
- 憑證管理
- 與 RBAC 整合

### Google Secret Manager

- GCP 原生方案
- 版本控管
- 與 IAM 整合

## HashiCorp Vault Integration

### Setup Vault

```bash
# Start Vault dev server
vault server -dev

# Set environment
export VAULT_ADDR='http://127.0.0.1:8200'
export VAULT_TOKEN='root'

# Enable secrets engine
vault secrets enable -path=secret kv-v2

# Store secret
vault kv put secret/database/config username=admin password=secret
```

### GitHub Actions with Vault

```yaml
name: Deploy with Vault Secrets

on: [push]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Import Secrets from Vault
        uses: hashicorp/vault-action@v2
        with:
          url: https://vault.example.com:8200
          token: ${{ secrets.VAULT_TOKEN }}
          secrets: |
            secret/data/database username | DB_USERNAME ;
            secret/data/database password | DB_PASSWORD ;
            secret/data/api key | API_KEY

      - name: Use secrets
        run: |
          echo "Connecting to database as $DB_USERNAME"
          # Use $DB_PASSWORD, $API_KEY
```

### GitLab CI with Vault

```yaml
deploy:
  image: vault:1.17
  before_script:
    - export VAULT_ADDR=https://vault.example.com:8200
    - export VAULT_TOKEN=$VAULT_TOKEN
    - apk add curl jq
  script:
    - |
      DB_PASSWORD=$(vault kv get -field=password secret/database/config)
      API_KEY=$(vault kv get -field=key secret/api/credentials)
      echo "Deploying with secrets..."
      # Use $DB_PASSWORD, $API_KEY
```

## AWS Secrets Manager

### Store Secret

```bash
aws secretsmanager create-secret \
  --name production/database/password \
  --secret-string "super-secret-password"
```

### Retrieve in GitHub Actions

```yaml
- name: Configure AWS credentials
  uses: aws-actions/configure-aws-credentials@v4
  with:
    aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
    aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
    aws-region: us-west-2

- name: Get secret from AWS
  run: |
    SECRET=$(aws secretsmanager get-secret-value \
      --secret-id production/database/password \
      --query SecretString \
      --output text)
    echo "::add-mask::$SECRET"
    echo "DB_PASSWORD=$SECRET" >> $GITHUB_ENV

- name: Use secret
  run: |
    # Use $DB_PASSWORD
    ./deploy.sh
```

### Terraform with AWS Secrets Manager

```hcl
data "aws_secretsmanager_secret_version" "db_password" {
  secret_id = "production/database/password"
}

resource "aws_db_instance" "main" {
  allocated_storage    = 100
  engine              = "postgres"
  instance_class      = "db.t3.large"
  username            = "admin"
  password            = jsondecode(data.aws_secretsmanager_secret_version.db_password.secret_string)["password"]
}
```

## GitHub Secrets

### Organization/Repository Secrets

```yaml
- name: Use GitHub secret
  env:
    API_KEY: ${{ secrets.API_KEY }}
    DATABASE_URL: ${{ secrets.DATABASE_URL }}
  run: |
    # Secrets are injected as env vars — never print them to logs
    ./deploy.sh
```

### Environment Secrets

```yaml
deploy:
  runs-on: ubuntu-latest
  environment: production
  steps:
    - name: Deploy
      env:
        PROD_API_KEY: ${{ secrets.PROD_API_KEY }}
      run: |
        # Secret injected as env var — never print to logs
        ./deploy.sh
```

## GitLab CI/CD Variables

### Project Variables

```yaml
deploy:
  script:
    # Fail if a variable is missing, but never print its value
    - test -n "$API_KEY" || { echo "API_KEY is not set"; exit 1; }
    - test -n "$DATABASE_URL" || { echo "DATABASE_URL is not set"; exit 1; }
```

### Protected and Masked Variables

- Protected：只能在受保護的 branch 使用
- Masked：在 job log 裡會被隱藏
- File type：以檔案形式儲存

## Best Practices

1. **絕對不要 commit secret** 到 Git
2. **每個環境用不同的 secret**
3. **定期輪替 secret**
4. **實作最小權限存取**
5. **啟用稽核 logging**
6. **用 secret 掃描**（GitGuardian、TruffleHog）
7. **在 log 裡遮蔽 secret**
8. **靜態加密 secret（encrypt at rest）**
9. **可以的話用短效 token**
10. **把 secret 的需求寫成文件**

## Secret Rotation

### Automated Rotation with AWS

```python
import boto3
import json

def lambda_handler(event, context):
    client = boto3.client('secretsmanager')

    # Get current secret
    response = client.get_secret_value(SecretId='my-secret')
    current_secret = json.loads(response['SecretString'])

    # Generate new password
    new_password = generate_strong_password()

    # Update database password
    update_database_password(new_password)

    # Update secret
    client.put_secret_value(
        SecretId='my-secret',
        SecretString=json.dumps({
            'username': current_secret['username'],
            'password': new_password
        })
    )

    return {'statusCode': 200}
```

### Manual Rotation Process

1. 產生新的 secret
2. 在 secret store 裡更新 secret
3. 更新應用程式改用新的 secret
4. 驗證功能正常
5. 撤銷舊的 secret

## External Secrets Operator

### Kubernetes Integration

```yaml
apiVersion: external-secrets.io/v1beta1
kind: SecretStore
metadata:
  name: vault-backend
  namespace: production
spec:
  provider:
    vault:
      server: "https://vault.example.com:8200"
      path: "secret"
      version: "v2"
      auth:
        kubernetes:
          mountPath: "kubernetes"
          role: "production"

---
apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
metadata:
  name: database-credentials
  namespace: production
spec:
  refreshInterval: 1h
  secretStoreRef:
    name: vault-backend
    kind: SecretStore
  target:
    name: database-credentials
    creationPolicy: Owner
  data:
    - secretKey: username
      remoteRef:
        key: database/config
        property: username
    - secretKey: password
      remoteRef:
        key: database/config
        property: password
```

## Secret Scanning

### Pre-commit Hook

```bash
#!/bin/bash
# .git/hooks/pre-commit

# Check for secrets with TruffleHog
docker run --rm -v "$(pwd):/repo" \
  trufflesecurity/trufflehog:3.88 \
  filesystem --directory=/repo

if [ $? -ne 0 ]; then
  echo "❌ Secret detected! Commit blocked."
  exit 1
fi
```

### CI/CD Secret Scanning

```yaml
secret-scan:
  stage: security
  image: trufflesecurity/trufflehog:3.88
  script:
    - trufflehog filesystem .
  allow_failure: false
```


## Related Skills

- `github-actions-templates` - 用於 GitHub Actions 整合
- `gitlab-ci-patterns` - 用於 GitLab CI 整合
- `deployment-pipeline-design` - 用於 pipeline 架構
