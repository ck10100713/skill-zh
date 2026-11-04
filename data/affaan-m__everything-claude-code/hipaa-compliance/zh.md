---
name: hipaa-compliance
description: 針對 HIPAA 的專用入口，處理醫療隱私與資安相關工作。當任務明確圍繞 HIPAA、PHI 處理、covered entity、BAA、資料外洩應對，或美國醫療法遵要求時使用。
metadata:
  version: "1.0.0"
  origin: ECC direct-port adaptation
---

# HIPAA Compliance

當任務明確是美國醫療法遵相關時，把這個當成 HIPAA 專用入口。這個 skill 刻意保持精簡，並以其他 skill 為準：

- `healthcare-phi-compliance` 仍然是 PHI/PII 處理、資料分級、audit logging、加密與防洩漏的主要實作 skill。
- 當程式碼、架構或產品行為需要具備醫療知識的二次檢查時，仍由 `healthcare-reviewer` 擔任專門的 reviewer。
- 一般的認證、輸入處理、secret、API 與部署強化，仍然適用 `security-review`。

## When to Use

- 需求明確提到 HIPAA、PHI、covered entity、business associate 或 BAA
- 開發或審查會儲存、處理、匯出或傳輸 PHI 的美國醫療軟體
- 評估 logging、analytics、LLM prompt、儲存或客服流程會不會造成 HIPAA 風險
- 設計面向病患或臨床人員的系統，而且最小必要存取和可稽核性很重要

## How It Works

把 HIPAA 當成疊在更廣泛的醫療隱私 skill 之上的一層：

1. 先用 `healthcare-phi-compliance` 取得具體的實作規則。
2. 套用 HIPAA 專屬的決策關卡：
   - 這筆資料是 PHI 嗎？
   - 這個角色是 covered entity 還是 business associate？
   - 廠商或模型供應商在碰資料之前，需要先簽 BAA 嗎？
   - 存取範圍有限縮到最小必要嗎？
   - 讀取、寫入、匯出事件都可稽核嗎？
3. 如果任務會影響病患安全、臨床流程或受法規管制的正式環境架構，就升級給 `healthcare-reviewer`。

## HIPAA-Specific Guardrails

- 絕對不准把 PHI 放進 log、analytics event、crash report、prompt 或使用者看得到的錯誤訊息。
- 絕對不准在 URL、瀏覽器儲存空間、截圖或複製出來的範例 payload 裡暴露 PHI。
- PHI 的讀取和寫入要有已認證的存取、限定範圍的授權和 audit trail。
- 第三方 SaaS、可觀測性工具、客服工具和 LLM 供應商，在 BAA 狀態和資料邊界釐清之前，一律預設封鎖。
- 遵守最小必要存取：對的使用者只能看到完成任務所需的最小 PHI 片段。
- 優先用不透明的內部 ID，不要用姓名、MRN、電話、地址或其他識別資訊。

## Examples

### Example 1: Product request framed as HIPAA

使用者需求：

> 在我們的臨床醫師儀表板加上 AI 產生的看診摘要。我們服務美國的診所，必須符合 HIPAA。

回應模式：

- 啟用 `hipaa-compliance`
- 用 `healthcare-phi-compliance` 檢查 PHI 的流向、logging、儲存和 prompt 邊界
- 在送出任何 PHI 之前，先確認摘要服務的供應商有沒有 BAA 涵蓋
- 如果摘要會影響臨床決策，就升級給 `healthcare-reviewer`

### Example 2: Vendor/tooling decision

使用者需求：

> 我們可以把客服對話紀錄和病患訊息送進分析系統嗎？

回應模式：

- 假設這些訊息可能含有 PHI
- 除非分析廠商已核准可處理受 HIPAA 約束的工作負載，而且資料路徑已縮到最小，否則封鎖這個設計
- 盡可能要求做遮蔽，或改用不含 PHI 的事件模型

## Related Skills

- `healthcare-phi-compliance`
- `healthcare-reviewer`
- `healthcare-emr-patterns`
- `healthcare-eval-harness`
- `security-review`
