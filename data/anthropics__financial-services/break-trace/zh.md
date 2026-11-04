---
name: break-trace
description: 把對帳差異（break）追查到根本原因，找出源頭的交易或過帳：沿著稽核軌跡，從差異那一列回溯到兩邊各自的原始分錄，說明哪裡不同、為什麼不同。在 gl-recon 已經把差異分類之後使用。
---

# 追查差異的根本原因

給定單一一列差異（key、GL 數值、subledger 數值、分類桶、可能的原因），把它追查到源頭，並產出根本原因的說明。

## 追查路徑

1. **取得 GL 那一邊**：透過 internal-gl MCP，抓出產生這筆 GL 明細的日記帳分錄或過帳：分錄 id、過帳日期、來源系統、批次 id、製作人。
2. **取得 subledger 那一邊**：透過 subledger MCP，抓出對應的交易：交易 id、交易/交割日期、交易對手、來源資料流、使用的匯率。
3. **比對屬性差異**：把過帳日期、匯率/匯率日期、科目對應、數量正負號、金額正負號對齊來看。不一樣的那個屬性通常就是原因。

## 原因 → 說明

把根本原因寫成一句話，格式為 **「⟨哪一邊⟩ ⟨做了什麼⟩ 因為 ⟨原因⟩」**，例如：

- "GL posted on settle date (T+2) while subledger posted on trade date — timing break, will clear on 2026-05-07."
- "Subledger used WM/R 4pm rate; GL used Bloomberg close — FX break of 12 bps on the base amount."
- "Security ABC123 maps to GL account 11420 in the mapping table but the subledger fed 11410 — mapping break, raise to reference-data."
- "Subledger posted the trade twice (trade ids 88412 and 88419 are duplicates) — duplicate post, suppress 88419."

## 輸出

每筆追查過的差異，回傳：

```json
{
  "key": "...",
  "root_cause": "one sentence as above",
  "owner": "ops | reference-data | accounting | upstream-system",
  "expected_clear_date": "YYYY-MM-DD or null",
  "action": "monitor | adjust | raise-ticket | suppress"
}
```

只有 resolver 可以寫入調整分錄，這個 skill 只負責診斷，不負責過帳。
