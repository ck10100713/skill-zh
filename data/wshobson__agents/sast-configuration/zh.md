---
name: sast-configuration
description: 設定靜態應用程式安全測試（SAST）工具，自動偵測應用程式碼中的漏洞。在設定安全掃描、落實 DevSecOps 實務，或自動化程式碼漏洞偵測時使用。
---

# SAST Configuration

靜態應用程式安全測試（SAST）工具的安裝、設定和自訂規則建立，針對多種程式語言做完整的安全掃描。

## Overview

這個 skill 提供完整的指引，教你安裝和設定 SAST 工具，包含 Semgrep、SonarQube 和 CodeQL。需要做以下事情時使用這個 skill：

- 在 CI/CD pipeline 裡設定 SAST 掃描
- 為你的 codebase 建立自訂的安全規則
- 設定 quality gate 和合規 policy
- 優化掃描效能並減少誤報
- 整合多個 SAST 工具做縱深防禦

## Core Capabilities

### 1. Semgrep Configuration

- 用 pattern matching 建立自訂規則
- 各語言專屬的安全規則（Python、JavaScript、Go、Java 等）
- CI/CD 整合（GitHub Actions、GitLab CI、Jenkins）
- 誤報調校和規則優化
- 組織層級的 policy 強制執行

### 2. SonarQube Setup

- Quality gate 設定
- 安全熱點（security hotspot）分析
- 程式碼覆蓋率和技術債追蹤
- 各語言的自訂 quality profile
- 跟 LDAP/SAML 做企業整合

### 3. CodeQL Analysis

- 整合 GitHub Advanced Security
- 自訂 query 開發
- 漏洞變體分析
- 安全研究工作流程
- SARIF 結果處理

## Quick Start

### Initial Assessment

1. 找出 codebase 的主要程式語言
2. 確定合規需求（PCI-DSS、SOC 2 等）
3. 依語言支援度和整合需求選擇 SAST 工具
4. 檢視 baseline 掃描，了解目前的安全狀況

### Basic Setup

```bash
# Semgrep quick start
pip install semgrep
semgrep --config=auto --error

# SonarQube with Docker
docker run -d --name sonarqube -p 9000:9000 sonarqube:10.8-community

# CodeQL CLI setup
gh extension install github/gh-codeql
codeql database create mydb --language=python
```

## Integration Patterns

### CI/CD Pipeline Integration

```yaml
# GitHub Actions example
- name: Run Semgrep
  uses: returntocorp/semgrep-action@v1
  with:
    config: >-
      p/security-audit
      p/owasp-top-ten
```

### Pre-commit Hook

```bash
# .pre-commit-config.yaml
- repo: https://github.com/returntocorp/semgrep
  rev: v1.45.0
  hooks:
    - id: semgrep
      args: ['--config=auto', '--error']
```

## Best Practices

1. **從 Baseline 開始**
   - 先跑一次初始掃描，建立安全 baseline
   - 優先處理 critical 和 high 等級的發現
   - 建立修復的路線圖

2. **漸進式採用**
   - 先從以安全為重點的規則開始
   - 逐步加入程式碼品質規則
   - 只對 critical 的問題實作阻擋

3. **誤報管理**
   - 把合理的 suppress 記錄成文件
   - 為已知安全的 pattern 建立允許清單
   - 定期檢視被 suppress 的發現

4. **效能優化**
   - 排除測試檔和產生的程式碼
   - 大型 codebase 用增量掃描
   - 在 CI/CD 快取掃描結果

5. **團隊賦能**
   - 為開發者提供安全訓練
   - 為常見的 pattern 建立內部文件
   - 建立 security champions 計畫

## Common Use Cases

### New Project Setup

```bash
# Semgrep: install, then run an auto-config scan that exits non-zero on findings
pip install semgrep
semgrep --config=auto --error

# SonarQube: start a community server for local evaluation, then analyze with sonar-scanner.
# SONAR_ES_BOOTSTRAP_CHECKS_DISABLE skips the Elasticsearch host checks for a local try-out;
# a real deployment needs vm.max_map_count>=524288 and fs.file-max>=131072 on the host instead.
docker run -d --name sonarqube -e SONAR_ES_BOOTSTRAP_CHECKS_DISABLE=true -p 9000:9000 sonarqube:10.8-community
```

### Custom Rule Development

```yaml
rules:
  - id: hardcoded-jwt-secret
    pattern: jwt.encode($DATA, "...", ...)
    message: JWT secret should not be hardcoded
    severity: ERROR
```

### Compliance Scanning

```bash
# PCI-DSS focused scan
semgrep --config p/pci-dss --json -o pci-scan-results.json
```

## Troubleshooting

### High False Positive Rate

- 檢視並調整規則的靈敏度
- 加上路徑 filter 來排除測試檔
- 對吵雜的 pattern 使用 nostmt metadata
- 建立組織專屬的規則例外

### Performance Issues

- 啟用增量掃描
- 跨模組平行執行掃描
- 優化規則 pattern 以提升效率
- 快取依賴和掃描結果

### Integration Failures

- 確認 API token 和憑證
- 檢查網路連線和 proxy 設定
- 檢視 SARIF 輸出格式的相容性
- 驗證 CI/CD runner 的權限

## Related Skills

- [STRIDE Analysis Patterns](../stride-analysis-patterns/SKILL.md)
- [Threat Mitigation Mapping](../threat-mitigation-mapping/SKILL.md)

## Tool Comparison

| Tool      | Best For                 | Language Support | Cost            | Integration   |
| --------- | ------------------------ | ---------------- | --------------- | ------------- |
| Semgrep   | 自訂規則、快速掃描 | 30+ languages    | Free/Enterprise | Excellent     |
| SonarQube | 程式碼品質 + 安全  | 25+ languages    | Free/Commercial | Good          |
| CodeQL    | 深度分析、研究  | 10+ languages    | Free (OSS)      | GitHub native |

## Next Steps

1. 完成 SAST 工具的初始設定
2. 跑 baseline 安全掃描
3. 為組織專屬的 pattern 建立自訂規則
4. 整合進 CI/CD pipeline
5. 建立 security gate 的 policy
6. 訓練開發團隊看懂掃描發現並修復
