---
name: django-verification
description: 跑完整的 Django 驗證流程：環境檢查、mypy/ruff/black lint、migration 安全、帶 coverage 目標的 pytest、pip-audit 與 bandit 安全掃描、設定與 logging 審查、diff 審查，並在發布或開 PR 前產出分階段的 pass/fail 報告。在準備 Django pull request、驗證 migration 或 coverage、或做部署前就緒檢查時使用。
metadata:
  origin: ECC
---

# Django 驗證流程

開 PR 前、大改動後、部署前都要跑，確保 Django 應用程式的品質與安全。

## 何時啟用

- 替 Django 專案開 pull request 之前
- model 大改、migration 更新或升級相依套件之後
- staging 或 production 的部署前驗證
- 跑完整的 環境 → lint → 測試 → 安全 → 部署就緒 流程
- 驗證 migration 安全與測試 coverage

## 階段 1：環境檢查

```bash
# Verify Python version
python --version  # Should match project requirements

# Check virtual environment
which python
pip list --outdated

# Verify environment variables
python -c "import os; import environ; print('DJANGO_SECRET_KEY set' if os.environ.get('DJANGO_SECRET_KEY') else 'MISSING: DJANGO_SECRET_KEY')"
```

如果環境設定有問題，先停下來修好。

## 階段 2：程式碼品質與格式

```bash
# Type checking
mypy . --config-file pyproject.toml

# Linting with ruff
ruff check . --fix

# Formatting with black
black . --check
black .  # Auto-fix

# Import sorting
isort . --check-only
isort .  # Auto-fix

# Django-specific checks
python manage.py check --deploy
```

常見問題：
- public function 缺少 type hint
- 違反 PEP 8 格式
- import 沒排序
- production 設定裡殘留 debug 設定

## 階段 3：Migration

```bash
# Check for unapplied migrations
python manage.py showmigrations

# Create missing migrations
python manage.py makemigrations --check

# Dry-run migration application
python manage.py migrate --plan

# Apply migrations (test environment)
python manage.py migrate

# Check for migration conflicts
python manage.py makemigrations --merge  # Only if conflicts exist
```

回報：
- 待套用的 migration 數量
- 有沒有 migration 衝突
- 有改 model 但沒產生 migration 的部分

## 階段 4：測試 + Coverage

```bash
# Run all tests with pytest
pytest --cov=apps --cov-report=html --cov-report=term-missing --reuse-db

# Run specific app tests
pytest apps/users/tests/

# Run with markers
pytest -m "not slow"  # Skip slow tests
pytest -m integration  # Only integration tests

# Coverage report
open htmlcov/index.html
```

回報：
- 測試總數：X 個通過、Y 個失敗、Z 個略過
- 整體 coverage：XX%
- 各 app 的 coverage 明細

Coverage 目標：

| 元件 | 目標 |
|-----------|--------|
| Models | 90%+ |
| Serializers | 85%+ |
| Views | 80%+ |
| Services | 90%+ |
| 整體 | 80%+ |

## 階段 5：安全掃描

```bash
# Dependency vulnerabilities
pip-audit
safety check --full-report

# Django security checks
python manage.py check --deploy

# Bandit security linter
bandit -r . -f json -o bandit-report.json

# Secret scanning (if gitleaks is installed)
gitleaks detect --source . --verbose

# Environment variable check
python -c "from django.core.exceptions import ImproperlyConfigured; from django.conf import settings; settings.DEBUG"
```

回報：
- 找到的有漏洞相依套件
- 安全設定問題
- 偵測到的寫死 secret
- DEBUG 模式狀態（production 應該是 False）

## 階段 6：Django 管理指令

```bash
# Check for model issues
python manage.py check

# Collect static files
python manage.py collectstatic --noinput --clear

# Create superuser (if needed for tests)
echo "from apps.users.models import User; User.objects.create_superuser('admin@example.com', 'admin')" | python manage.py shell

# Database integrity
python manage.py check --database default

# Cache verification (if using Redis)
python -c "from django.core.cache import cache; cache.set('test', 'value', 10); print(cache.get('test'))"
```

## 階段 7：效能檢查

```bash
# Django Debug Toolbar output (check for N+1 queries)
# Run in dev mode with DEBUG=True and access a page
# Look for duplicate queries in SQL panel

# Query count analysis
django-admin debugsqlshell  # If django-debug-sqlshell installed

# Check for missing indexes
python manage.py shell << EOF
from django.db import connection
with connection.cursor() as cursor:
    cursor.execute("SELECT table_name, index_name FROM information_schema.statistics WHERE table_schema = 'public'")
    print(cursor.fetchall())
EOF
```

回報：
- 每頁的 query 數（一般頁面應 < 50）
- 缺少的資料庫 index
- 偵測到的重複 query

## 階段 8：靜態資源

```bash
# Check for npm dependencies (if using npm)
npm audit
npm audit fix

# Build static files (if using webpack/vite)
npm run build

# Verify static files
ls -la staticfiles/
python manage.py findstatic css/style.css
```

## 階段 9：設定審查

```python
# Run in Python shell to verify settings
python manage.py shell << EOF
from django.conf import settings
import os

# Critical checks
checks = {
    'DEBUG is False': not settings.DEBUG,
    'SECRET_KEY set': bool(settings.SECRET_KEY and len(settings.SECRET_KEY) > 30),
    'ALLOWED_HOSTS set': len(settings.ALLOWED_HOSTS) > 0,
    'HTTPS enabled': getattr(settings, 'SECURE_SSL_REDIRECT', False),
    'HSTS enabled': getattr(settings, 'SECURE_HSTS_SECONDS', 0) > 0,
    'Database configured': settings.DATABASES['default']['ENGINE'] != 'django.db.backends.sqlite3',
}

for check, result in checks.items():
    status = '✓' if result else '✗'
    print(f"{status} {check}")
EOF
```

## 階段 10：Logging 設定

```bash
# Test logging output
python manage.py shell << EOF
import logging
logger = logging.getLogger('django')
logger.warning('Test warning message')
logger.error('Test error message')
EOF

# Check log files (if configured)
tail -f /var/log/django/django.log
```

## 階段 11：API 文件（如果用 DRF）

```bash
# Generate schema
python manage.py generateschema --format openapi-json > schema.json

# Validate schema
# Check if schema.json is valid JSON
python -c "import json; json.load(open('schema.json'))"

# Access Swagger UI (if using drf-yasg)
# Visit http://localhost:8000/swagger/ in browser
```

## 階段 12：Diff 審查

```bash
# Show diff statistics
git diff --stat

# Show actual changes
git diff

# Show changed files
git diff --name-only

# Check for common issues
git diff | grep -i "todo\|fixme\|hack\|xxx"
git diff | grep "print("  # Debug statements
git diff | grep "DEBUG = True"  # Debug mode
git diff | grep "import pdb"  # Debugger
```

檢查清單：
- 沒有除錯用的程式碼（print、pdb、breakpoint()）
- 重要程式碼裡沒有 TODO/FIXME 註解
- 沒有寫死的 secret 或憑證
- 有改 model 就要附上資料庫 migration
- 設定變更有記錄
- 呼叫外部服務的地方有錯誤處理
- 需要的地方有做 transaction 管理

## 輸出範本

```
DJANGO VERIFICATION REPORT
==========================

Phase 1: Environment Check
  ✓ Python 3.11.5
  ✓ Virtual environment active
  ✓ All environment variables set

Phase 2: Code Quality
  ✓ mypy: No type errors
  ✗ ruff: 3 issues found (auto-fixed)
  ✓ black: No formatting issues
  ✓ isort: Imports properly sorted
  ✓ manage.py check: No issues

Phase 3: Migrations
  ✓ No unapplied migrations
  ✓ No migration conflicts
  ✓ All models have migrations

Phase 4: Tests + Coverage
  Tests: 247 passed, 0 failed, 5 skipped
  Coverage:
    Overall: 87%
    users: 92%
    products: 89%
    orders: 85%
    payments: 91%

Phase 5: Security Scan
  ✗ pip-audit: 2 vulnerabilities found (fix required)
  ✓ safety check: No issues
  ✓ bandit: No security issues
  ✓ No secrets detected
  ✓ DEBUG = False

Phase 6: Django Commands
  ✓ collectstatic completed
  ✓ Database integrity OK
  ✓ Cache backend reachable

Phase 7: Performance
  ✓ No N+1 queries detected
  ✓ Database indexes configured
  ✓ Query count acceptable

Phase 8: Static Assets
  ✓ npm audit: No vulnerabilities
  ✓ Assets built successfully
  ✓ Static files collected

Phase 9: Configuration
  ✓ DEBUG = False
  ✓ SECRET_KEY configured
  ✓ ALLOWED_HOSTS set
  ✓ HTTPS enabled
  ✓ HSTS enabled
  ✓ Database configured

Phase 10: Logging
  ✓ Logging configured
  ✓ Log files writable

Phase 11: API Documentation
  ✓ Schema generated
  ✓ Swagger UI accessible

Phase 12: Diff Review
  Files changed: 12
  +450, -120 lines
  ✓ No debug statements
  ✓ No hardcoded secrets
  ✓ Migrations included

RECOMMENDATION: WARNING: Fix pip-audit vulnerabilities before deploying

NEXT STEPS:
1. Update vulnerable dependencies
2. Re-run security scan
3. Deploy to staging for final testing
```

## 部署前檢查清單

- [ ] 所有測試通過
- [ ] Coverage ≥ 80%
- [ ] 沒有安全漏洞
- [ ] 沒有未套用的 migration
- [ ] production 設定裡 DEBUG = False
- [ ] SECRET_KEY 設定正確
- [ ] ALLOWED_HOSTS 設定正確
- [ ] 已開啟資料庫備份
- [ ] 靜態檔案已收集並正常提供
- [ ] Logging 已設定且正常運作
- [ ] 已設定錯誤監控（Sentry 等）
- [ ] 已設定 CDN（如果適用）
- [ ] 已設定 Redis/cache backend
- [ ] Celery worker 有在跑（如果適用）
- [ ] 已設定 HTTPS/SSL
- [ ] 環境變數已有文件

## 持續整合（CI）

### GitHub Actions 範例

```yaml
# .github/workflows/django-verification.yml
name: Django Verification

on: [push, pull_request]

jobs:
  verify:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:14
        env:
          POSTGRES_PASSWORD: postgres
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Cache pip
        uses: actions/cache@v3
        with:
          path: ~/.cache/pip
          key: ${{ runner.os }}-pip-${{ hashFiles('**/requirements.txt') }}

      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install ruff black mypy pytest pytest-django pytest-cov bandit safety pip-audit

      - name: Code quality checks
        run: |
          ruff check .
          black . --check
          isort . --check-only
          mypy .

      - name: Security scan
        run: |
          bandit -r . -f json -o bandit-report.json
          safety check --full-report
          pip-audit

      - name: Run tests
        env:
          DATABASE_URL: postgres://postgres:postgres@localhost:5432/test
          DJANGO_SECRET_KEY: test-secret-key
        run: |
          pytest --cov=apps --cov-report=xml --cov-report=term-missing

      - name: Upload coverage
        uses: codecov/codecov-action@v3
```

## 快速參考

| 檢查項目 | 指令 |
|-------|---------|
| 環境 | `python --version` |
| 型別檢查 | `mypy .` |
| Lint | `ruff check .` |
| 格式化 | `black . --check` |
| Migration | `python manage.py makemigrations --check` |
| 測試 | `pytest --cov=apps` |
| 安全 | `pip-audit && bandit -r .` |
| Django check | `python manage.py check --deploy` |
| Collectstatic | `python manage.py collectstatic --noinput` |
| Diff 統計 | `git diff --stat` |

記住：自動化驗證能抓到常見問題，但不能取代人工 code review 和在 staging 環境的測試。
