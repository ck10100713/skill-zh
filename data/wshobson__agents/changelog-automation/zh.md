---
name: changelog-automation
description: 依 Keep a Changelog 格式，從 commit、PR 和 release 自動產生 changelog。在設定 release 工作流程、產生 release note，或統一 commit 慣例時使用。
---

# Changelog 自動化

依業界標準，自動化產生 changelog、release note 和版本管理的模式與工具。

## 何時使用這個 Skill

- 設定自動化的 changelog 產生
- 實作 Conventional Commits
- 建立 release note 的工作流程
- 統一 commit 訊息格式
- 產生 GitHub/GitLab 的 release note
- 管理語意化版本（semantic versioning）

## 核心概念

### 1. Keep a Changelog 格式

```markdown
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## Detailed patterns and worked examples

Detailed pattern documentation lives in `references/details.md`. Read that file when the navigation tier above is insufficient.

## Summary

This release introduces dark mode support and improves checkout performance
by 40%. It also includes important security updates.

## Highlights

### 🌙 Dark Mode

Users can now switch to dark mode from settings. The preference is
automatically saved and synced across devices.

### ⚡ Performance

- Checkout flow is 40% faster
- Reduced bundle size by 15%

## Breaking Changes

None in this release.

## Upgrade Guide

No special steps required. Standard deployment process applies.

## Known Issues

- Dark mode may flicker on initial load (fix scheduled for v2.1.1)

## Dependencies Updated

| Package | From    | To      | Reason                   |
| ------- | ------- | ------- | ------------------------ |
| react   | 18.2.0  | 18.3.0  | Performance improvements |
| lodash  | 4.17.20 | 4.17.21 | Security patch           |
```

## Commit 訊息範例

```bash
# Feature with scope
feat(auth): add OAuth2 support for Google login

# Bug fix with issue reference
fix(checkout): resolve race condition in payment processing

Closes #123

# Breaking change
feat(api)!: change user endpoint response format

BREAKING CHANGE: The user endpoint now returns `userId` instead of `id`.
Migration guide: Update all API consumers to use the new field name.

# Multiple paragraphs
fix(database): handle connection timeouts gracefully

Previously, connection timeouts would cause the entire request to fail
without retry. This change implements exponential backoff with up to
3 retries before failing.

The timeout threshold has been increased from 5s to 10s based on p99
latency analysis.

Fixes #456
Reviewed-by: @alice
```

## 最佳實務

### 該做的

- **遵循 Conventional Commits** - 才能自動化
- **寫清楚的訊息** - 未來的你會感謝現在的你
- **引用 issue** - 把 commit 連到 ticket
- **一致地使用 scope** - 定義團隊的慣例
- **自動化 release** - 減少人工錯誤

### 不該做的

- **不要混在一起改** - 一個 commit 只放一個邏輯上的變更
- **不要跳過驗證** - 用 commitlint
- **不要手動編輯** - changelog 只能由工具產生
- **不要忘了破壞性變更** - 用 `!` 或 footer 標記
- **不要忽略 CI** - 在 pipeline 裡驗證 commit
