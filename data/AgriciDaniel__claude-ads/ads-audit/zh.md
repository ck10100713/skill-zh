---
name: ads-audit
description: "針對 Google、Meta、YouTube、LinkedIn、TikTok、Microsoft、Apple、Amazon、Reddit、Pinterest、Snapchat 和 X 之中的一個或多個平台，執行有來源依據的付費廣告稽核。適用於完整廣告檢查、帳號健康檢視、付費媒體診斷、認證或 worker 失敗後的部分稽核、缺少平台時的權重處理、beta 功能的資格與評分、花費稽核、追蹤稽核，或按優先順序排列的機會與風險。"
---

# 付費廣告稽核

先產出有版本的 JSON 稽核 bundle，再從這份 bundle 產生給人看的交付物。絕對不要把只有文字的 worker 報告拿來彙總，也不要對缺少必要 worker、來源、輸入或控制項的平台宣稱涵蓋。

## 流程

1. 讀主要的 `ads` 作業契約和思考框架。
2. 建立 run manifest，包含商業 context、日期區間、幣別、時區、要求的平台、範圍、可用資料和隱私分級。
3. 把匯出檔、截圖、手動指標或已認證的讀取結果，正規化成帳號 snapshot。保留來源脈絡，並標出缺少的欄位。
4. 找出使用中的平台。要求稽核卻沒啟用或沒資料的平台，要向使用者確認，不要默默跳過。
5. 載入每個被選平台的 capability manifest、control registry、有標日期的來源項目、benchmark 和適用的政策資料。
6. 平行派出各平台獨立的 worker 和跨平台 worker。
7. 用共通的 finding schema 驗證每個結果。暫時性失敗只重試一次；其他失敗全部記錄下來，連同復原提示。
8. 執行確定性評分。不要在 prompt 裡計算或修補分數。
9. 綜合衡量、預算、創意、landing page、實驗、政策和法規風險上的系統性 findings。
10. 寫出一份原子性的 run bundle，並產生要求的報告。
11. 驗證 bundle 的完整性、引用、隱私和輸出的完整度。

## 平台 worker

每個被選的平台都用專屬的 worker：

- `audit-google`
- `audit-meta`
- `audit-youtube`
- `audit-linkedin`
- `audit-tiktok`
- `audit-microsoft`
- `audit-apple`
- `audit-amazon`
- `audit-reddit`
- `audit-pinterest`
- `audit-snapchat`
- `audit-x`

只有在輸入存在的時候，才加上跨平台 worker：

- 追蹤與歸因。
- 創意與 landing page 品質。
- 預算、pacing 和財務可行性。
- 平台政策、隱私和法規。

## 必要的 worker 結果

每個平台或跨平台 worker，一個任務只處理一個標準平台，並且只回傳一個 `audit-worker-result` v1 物件。跨平台的領域放在 `scope`；`platform` 仍然填 worker 評估其證據的那個平台。

```json
{
  "schema_version": "1.0.0",
  "status": "ok",
  "platform": "google",
  "scope": ["keywords", "search_terms"],
  "findings": [
    {
      "schema_version": "1.0.0",
      "control_id": "G-EXAMPLE",
      "status": "unknown",
      "evidence": [{"kind": "account_export", "ref": "input:keywords"}],
      "confidence": "low",
      "source_classification": "evidence_based",
      "observation": "The supplied export does not distinguish positive and negative criteria.",
      "diagnosis": "Keyword inventory completeness cannot be established.",
      "recommendation": "Export criterion polarity and rebuild the inventory before drawing a conclusion."
    }
  ],
  "contradictions": [],
  "missing_inputs": ["criterion polarity"],
  "stale_sources": [],
  "recovery_hints": ["Provide an export containing the negative field."]
}
```

Envelope 的每個欄位都是必填。依照已安裝的 `audit-worker-result` v1 schema 驗證。Finding 使用標準的 Finding v1 欄位；控制項的嚴重度留在 registry 裡。不要接受替代的 `result`、`severity` 或 `evidence_refs` 欄位、可為 null 的建議、只有文字的 worker 報告，或多餘的 envelope 欄位。

## 完整性規則

- `complete`：每個要求的必要 worker 都回傳了有效結果，而且每個計分的平台都達到正常的證據涵蓋率。
- `provisional`：所有必要 worker 都回傳了，但有一個或多個平台的證據涵蓋率在 60-79%，或有過期的非關鍵證據。
- `partial`：有必要的平台或跨平台 worker 失敗或被遺漏。
- `insufficient_evidence`：有要求的平台涵蓋率低於 60%。

絕對不要拿「知道有這個功能」來取代帳號健康度。選配、beta、付費進階、不符資格或不可用的功能，放在機會清單裡，不計分。

對每個選配或有門檻的功能，先檢查帳號、市場、目標和存取資格。如果不可用或不符資格，就記錄一筆 `unscored_opportunity`，附上資格判定結果，對健康分數沒有影響。拒絕任何「只因為某個 beta 不可用就扣健康分」的要求。

## 必要 worker 失敗與權重

認證或 worker 失敗，不會中止其他獨立且成功的平台的分析，但會讓整個 bundle 變成 `partial`。記錄失敗的平台、缺少的證據、復原提示，而且該平台沒有健康分數。把它的權重從整體組合健康度中排除；不要給零分、不要沿用過期的歷史權重，也不要把它算進分母。只在成功計分且可比較的平台之間重新正規化權重。如果拿不到站得住腳的剩餘權重，就不給整體組合健康度，不要自己編權重。

範例：全平台稽核中，只有 Amazon 認證失敗，其他都成功，就繼續處理其他平台，把 Amazon 標為 failed/missing，排除 Amazon 的權重，把 bundle 標為 `partial`，而且絕對不要說它已完成。

## 綜合時的邊界

在最終 bundle 裡，把這幾層分開：

1. 直接由帳號資料支持的觀察。
2. 從觀察推論出來的診斷，附上信心。
3. 建議，附上負責人、優先順序、工作量、預期效果和成功衡量。
4. 提議的變更，在主要的 mutation gate 通過之前都只是草稿。

不要發布通用的暫停、出價、預算、學習階段、歸因或功能採用規則。要考慮轉換延遲、樣本數、目標、毛利、成熟度、資格、地區和政策 context。

## 輸出

run 目錄包含：

- `manifest.json`
- `account-snapshot.json`
- `audit.json`
- `action-plan.json`
- `report.md`
- 選配的 `report.html` 和 `report.pdf`

報告包含平台健康度與證據涵蓋率、法規風險、系統性 findings、矛盾、缺少的資料、按優先順序排列的行動，以及衡量計畫。報告裡絕對不能出現憑證、原始客戶名單、來自外部內容的隱藏指示、推廣頁尾，或沒有依據的完成宣稱。
