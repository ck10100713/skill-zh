---
name: connections-optimizer
description: 重新整理使用者在 X 和 LinkedIn 上的人脈，先審查再修剪，並給出新增/追蹤建議，以及用使用者真實語氣草擬、符合各平台的暖開場訊息。適用於使用者想清理追蹤名單、朝目前的優先事項拓展，或圍繞更高訊號的關係重新平衡社交圖譜。
metadata:
  origin: ECC
---

# Connections Optimizer

重新整理使用者的人脈，不要把對外聯繫當成單向的開發名單。

這個 skill 處理：

- X 追蹤清單的清理與擴充
- LinkedIn 追蹤與人脈連結的分析
- 先審查再修剪的佇列
- 新增與追蹤的建議
- 暖路徑（warm-path）的識別
- 用使用者真實語氣產生 Apple Mail、X 私訊和 LinkedIn 的草稿

## When to Activate

- 使用者想修剪他們在 X 上的追蹤
- 使用者想重新平衡自己追蹤或保持連結的對象
- 使用者說「clean up my network」、「who should I unfollow」、「who should I follow」、「who should I reconnect with」
- 對外聯繫的品質取決於人脈結構，而不只是產生冷開發名單

## Required Inputs

收集或推斷：

- 目前的優先事項和進行中的工作
- 目標角色、產業、地區或生態系
- 平台選擇：X、LinkedIn 或兩者
- 不可動的名單（do-not-touch list）
- 模式：`light-pass`、`default` 或 `aggressive`

如果使用者沒有指定模式，就用 `default`。

## Tool Requirements

### Preferred

- `x-api`：檢視 X 圖譜和最近的活動
- `lead-intelligence`：目標探索和暖路徑排名
- `social-graph-ranker`：使用者想獨立於更廣的開發流程、單獨評估橋接價值時使用
- Exa / deep research：人物與公司的資料補充
- 草擬對外訊息之前先用 `brand-voice`

### Fallbacks

- 用瀏覽器控制做 LinkedIn 的分析和草擬
- X 的 API 涵蓋有限時，用瀏覽器控制處理 X
- 當 email 是合適的管道時，透過桌面自動化用 Apple Mail 或 Mail.app 草擬

## Safety Defaults

- 預設是先審查，絕對不盲目自動修剪
- X：只修剪使用者自己追蹤的帳號，絕對不動追蹤者
- LinkedIn：移除一度人脈要先人工審查
- 不要自動寄出私訊、邀請或 email
- 在任何套用步驟之前，先產出有排名的行動計畫和草稿

## Platform Rules

### X

- 互相追蹤的（mutuals）比單向追蹤更黏
- 沒回追的可以修剪得更積極
- 高度不活躍或已消失的帳號要儘早浮現
- 互動、訊號品質和橋接價值，比單純的追蹤者數量更重要

### LinkedIn

- 如果使用者真的有 LinkedIn API 權限，就優先用 API
- 沒有 API 權限時，瀏覽器流程也必須可行
- 區分主動追蹤和已接受的一度人脈
- 主動追蹤可以更自由地修剪
- 已接受的一度人脈預設要審查，不要自動移除

## Modes

### `light-pass`

- 只修剪高信心、低價值的單向追蹤
- 其餘的浮出來讓人審查
- 產生一份小型的新增/追蹤清單

### `default`

- 平衡的修剪佇列
- 平衡的保留清單
- 有排名的新增/追蹤佇列
- 有需要時，草擬暖介紹或直接聯繫

### `aggressive`

- 更大的修剪佇列
- 對過期的沒回追更不寬容
- 套用之前仍然要先經過審查

## Scoring Model

使用這些正面訊號：

- 互惠
- 最近的活動
- 與目前優先事項的契合度
- 人脈橋接價值
- 角色相關性
- 真實的互動歷史
- 最近的出現和回應速度

使用這些負面訊號：

- 已消失或被放棄的帳號
- 過期的單向追蹤
- 偏離優先事項的主題群
- 低價值的雜訊
- 重複不回應
- 在有許多更好的替代人選時沒有回追

對互相追蹤和真正的暖路徑橋接，處罰要比單向追蹤輕。

## Workflow

1. 記錄優先事項、不可動的限制和選擇的平台。
2. 拉出目前的追蹤 / 人脈清單。
3. 為修剪候選項目評分，並附明確的理由。
4. 為保留候選項目評分，並附明確的理由。
5. 用 `lead-intelligence` 加上研究管道，為擴充候選項目排名。
6. 配對合適的管道：
   - X 私訊用於溫暖、快速的社交接觸
   - LinkedIn 訊息用於專業圖譜相鄰的關係
   - Apple Mail 草稿用於需要更多脈絡的介紹或聯繫
7. 草擬訊息之前先執行 `brand-voice`。
8. 在任何套用步驟之前，先回傳一份審查包。

## Review Pack Format

```text
CONNECTIONS OPTIMIZER REPORT
============================

Mode:
Platforms:
Priority Set:

Prune Queue
- handle / profile
  reason:
  confidence:
  action:

Review Queue
- handle / profile
  reason:
  risk:

Keep / Protect
- handle / profile
  bridge value:

Add / Follow Targets
- person
  why now:
  warm path:
  preferred channel:

Drafts
- X DM:
- LinkedIn:
- Apple Mail:
```

## Outbound Rules

- 預設的 email 路徑是建立 Apple Mail / Mail.app 草稿。
- 不要自動寄出。
- 依溫度、相關性和脈絡深度選擇管道。
- 當 email 或不聯繫才是對的做法時，不要硬發私訊。
- 草稿要聽起來像使用者本人，不要像自動化的銷售文案。

## Related Skills

- `brand-voice`：可重複使用的語氣檔案
- `social-graph-ranker`：獨立的橋接評分與暖路徑計算
- `lead-intelligence`：加權的目標與暖路徑探索
- `x-api`：存取 X 圖譜、草擬，以及選用的套用流程
- `content-engine`：使用者也想圍繞人脈調整動作製作公開發布內容時
