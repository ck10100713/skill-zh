---
name: canary-watch
description: 發布後用這個 skill 監控並驗證已部署的 URL，在部署、merge 或依賴升級之後，檢查 HTTP endpoint、SSE 串流、靜態資源、console 錯誤和效能退化。屬於冒煙測試 / canary / 部署後驗證。
metadata:
  origin: ECC
---

# Canary Watch — Post-Deploy Monitoring

## When to Use

- 部署到 production 或 staging 之後
- merge 了有風險的 PR 之後
- 想確認某個修正真的修好了
- 上線時段的持續監控
- 依賴升級之後

## How It Works

監控已部署的 URL 有沒有退化。持續循環執行，直到被停止或監看時間到期。

### What It Watches

```
1. HTTP Status — is the page returning 200?
2. Console Errors — new errors that weren't there before?
3. Network Failures — failed API calls, 5xx responses?
4. Performance — LCP/CLS/INP regression vs baseline?
5. Content — did key elements disappear? (h1, nav, footer, CTA)
6. API Health — are critical endpoints responding within SLA?
7. Static Assets — are JS, CSS, image, and font requests returning 2xx/3xx with expected content types?
8. SSE Streams — do event-stream endpoints connect and receive an initial event or heartbeat?
```

### Watch Modes

**快速檢查**（預設）：跑一輪，回報結果
```
/canary-watch https://myapp.com
```

**持續監看**：每 N 分鐘檢查一次，持續 M 小時
```
/canary-watch https://myapp.com --interval 5m --duration 2h
```

**Diff 模式**：比較 staging 和 production
```
/canary-watch --compare https://staging.myapp.com https://myapp.com
```

### Alert Thresholds

```yaml
critical:  # immediate alert
  - HTTP status != 200
  - Console error count > 5 (new errors only)
  - LCP > 4s
  - API endpoint returns 5xx
  - Static asset returns 4xx/5xx
  - SSE endpoint cannot connect or drops before first heartbeat

warning:   # flag in report
  - LCP increased > 500ms from baseline
  - CLS > 0.1
  - New console warnings
  - Response time > 2x baseline
  - Static asset content type changed unexpectedly
  - SSE heartbeat latency > 2x baseline

info:      # log only
  - Minor performance variance
  - New network requests (third-party scripts added?)
```

### Notifications

超過 critical 門檻時：
- 桌面通知（macOS/Linux）
- 選用：Slack/Discord webhook
- 記錄到 `~/.claude/canary-watch.log`

## Output

```markdown
## Canary Report — myapp.com — 2026-03-23 03:15 PST

### Status: HEALTHY ✓

| Check | Result | Baseline | Delta |
|-------|--------|----------|-------|
| HTTP | 200 ✓ | 200 | — |
| Console errors | 0 ✓ | 0 | — |
| LCP | 1.8s ✓ | 1.6s | +200ms |
| CLS | 0.01 ✓ | 0.01 | — |
| API /health | 145ms ✓ | 120ms | +25ms |
| Static assets | 42/42 ✓ | 42/42 | — |
| SSE /events | connected ✓ | connected | +80ms heartbeat |

### No regressions detected. Deploy is clean.
```

## Integration

可以搭配：
- `/browser-qa` 做部署前的驗證
- Hooks：加成 `git push` 上的 PostToolUse hook，部署後自動檢查
- CI：在 GitHub Actions 的部署步驟之後執行
