---
name: security-bounty-hunter
description: 在 repo 中獵找可被利用、值得領獎金的安全問題。聚焦在能遠端觸及、夠格提交真正報告的漏洞，不理會只有本機才成立、雜訊多的發現。在 repo 裡獵找可回報、可遠端觸及的漏洞時使用。
metadata:
  version: "1.0.0"
  origin: ECC direct-port adaptation
---

# Security Bounty Hunter

目標是為了負責任揭露或提交獎金而實際發現漏洞，不是廣泛的最佳實務檢視時，使用這個 skill。

## 何時使用

- 掃描 repo，找可被利用的漏洞
- 準備 Huntr、HackerOne 或類似平台的獎金提交
- 分級（triage）時，問題是「這個真的有賞金嗎？」，而不是「這在理論上不安全嗎？」

## 運作方式

偏向遠端可觸及、使用者可控的攻擊路徑，並丟掉平台經常以資訊性或超出範圍為由退回的模式。

## 範圍內的模式

這些是一直都很重要的問題類型：

| 模式 | CWE | 典型影響 |
| --- | --- | --- |
| 透過使用者可控 URL 的 SSRF | CWE-918 | 存取內部網路、竊取雲端 metadata |
| middleware 或 API 防護中的驗證繞過 | CWE-287 | 未授權存取帳號或資料 |
| 遠端反序列化或上傳到 RCE 的路徑 | CWE-502 | 程式碼執行 |
| 可觸及 endpoint 中的 SQL injection | CWE-89 | 資料外洩、驗證繞過、資料毀損 |
| request handler 中的指令注入 | CWE-78 | 程式碼執行 |
| 檔案服務路徑中的 path traversal | CWE-22 | 任意檔案讀取或寫入 |
| 自動觸發的 XSS | CWE-79 | 竊取 session、入侵管理員 |

## 要跳過的

除非該計畫另有說明，這些通常訊號太弱，或超出獎金範圍：

- 只有本機才成立的 `pickle.loads`、`torch.load` 或同類寫法，沒有遠端路徑
- 只出現在 CLI 工具裡的 `eval()` 或 `exec()`
- 指令完全寫死的 `shell=True`
- 單純缺少安全 header
- 沒有實際利用影響的泛泛 rate-limiting 抱怨
- 需要受害者自己手動貼程式碼的 Self-XSS
- 不屬於目標計畫範圍的 CI/CD injection
- Demo、範例或只用於測試的程式碼

## 工作流程

1. 先確認範圍：計畫規則、SECURITY.md、揭露管道和排除項目。
2. 找出真正的入口：HTTP handler、上傳、背景工作、webhook、parser 和整合 endpoint。
3. 有幫助的地方就跑靜態分析工具，但只把它當成分級的輸入。
4. 把真正的程式碼路徑從頭讀到尾。
5. 證明使用者的控制能到達有意義的 sink。
6. 用盡可能小、安全的 PoC 確認可利用性與影響。
7. 起草報告之前先檢查有沒有重複。

## 分級迴圈範例

```bash
semgrep --config=auto --severity=ERROR --severity=WARNING --json
```

然後手動過濾：

- 丟掉測試、demo、fixture、vendored 程式碼
- 丟掉只有本機才成立或無法觸及的路徑
- 只留下有明確網路或使用者可控路徑的發現

## 報告結構

```markdown
## Description
[What the vulnerability is and why it matters]

## Vulnerable Code
[File path, line range, and a small snippet]

## Proof of Concept
[Minimal working request or script]

## Impact
[What the attacker can achieve]

## Affected Version
[Version, commit, or deployment target tested]
```

## 品質關卡

提交之前：

- 程式碼路徑可以從真實使用者或網路邊界觸及
- 輸入確實由使用者控制
- Sink 有意義而且可利用
- PoC 能跑
- 這個問題還沒被 advisory、CVE 或公開的 ticket 涵蓋
- 目標確實在獎金計畫的範圍內
