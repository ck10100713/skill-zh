---
name: hads
description: 適用於撰寫人類和 AI 模型都讀得懂的技術文件、把既有文件轉成 HADS 格式、驗證 HADS 文件，或針對 AI 讀取最佳化文件的 token 效率的時候。
---

# HADS Claude Skill
**版本 1.0.0** · Human-AI Document Standard · 2026 · HADS 1.0.0

---

## AI READING INSTRUCTION（AI 閱讀指示）

這個 skill 教 Claude 如何讀取、產生與驗證 HADS 文件。
回應任何與 HADS 相關的請求之前，先讀完所有 `[SPEC]` 區塊。
如果需要了解意圖或邊界情況的脈絡，就讀 `[NOTE]` 區塊。

---

## 1. 什麼是 HADS

**[SPEC]**
- HADS = Human-AI Document Standard
- Markdown 技術文件的一種慣例
- 四種區塊類型：`**[SPEC]**`、`**[NOTE]**`、`**[BUG]**`、`**[?]**`
- 每份 HADS 文件都必須有：H1 標題、版本宣告、AI manifest
- AI manifest 出現在第一個內容章節之前，告訴 AI 該讀什麼、該跳過什麼
- 副檔名：`.md`，標準的 Markdown，不需要任何工具

---

## 2. 區塊類型

**[SPEC]**
```
**[SPEC]**   權威的事實。精簡。條列、表格、程式碼。AI 一律會讀。
**[NOTE]**   給人看的脈絡、歷史、範例。AI 可以跳過。
**[BUG]**    已驗證的失敗與修法。必填欄位：symptom、cause、fix。一律要讀。
**[?]**      未驗證/推論出來的內容。信心較低。一律要標示。
```

區塊標籤規則：
- 粗體，單獨一行：`**[SPEC]**`
- 內容緊接在後（標籤與內容之間沒有空行）
- 每個章節可以有多個不同類型的區塊
- 可以有帶標題的 BUG 區塊：`**[BUG] Short description**`
- 區塊內不可以再巢狀放區塊

---

## 3. 必要的文件結構

**[SPEC]**
```markdown
# Document Title
**Version X.Y.Z** · Author · Date · [metadata]

---

## AI READING INSTRUCTION

Read `[SPEC]` and `[BUG]` blocks for authoritative facts.
Read `[NOTE]` only if additional context is needed.
`[?]` blocks are unverified — treat with lower confidence.

---

## 1. First Section

**[SPEC]**
...
```

依序必須具備的元素：
1. H1 標題
2. header 中有 `**Version X.Y.Z**`（前 20 行內）
3. 在第一個內容章節之前有 AI manifest 章節
4. 內容章節（H2）、子章節（H3）

---

## 4. Claude 如何讀取 HADS

**[SPEC]**
遇到 HADS 文件時：
1. 先找到並讀取 AI manifest
2. 讀所有 `[SPEC]` 區塊，這些是 ground truth
3. 讀所有 `[BUG]` 區塊，產生任何程式碼或設定之前一定要讀
4. 只有在 `[SPEC]` 不足以回答問題時，才讀 `[NOTE]` 區塊
5. 把 `[?]` 的內容當作假設，並在回應中註明不確定性

Token 最佳化：對於大型文件，先掃描章節標題，再只讀相關章節中的 `[SPEC]` 和 `[BUG]` 區塊。

---

## 5. Claude 如何產生 HADS

**[SPEC]**
被要求用 HADS 格式撰寫文件時：

1. 從 header 區塊開始（標題、版本、metadata）
2. 加上 AI manifest，一定要加，不准省略
3. 把內容整理成有編號的 H2 章節
4. 每一項事實都寫成 `[SPEC]`：精簡，用條列、表格或程式碼
5. 每一項「為什麼」或脈絡都寫成 `[NOTE]`
6. 每一個已知且有確認修法的失敗模式都寫成 `[BUG]`
7. 每一項未驗證的主張都寫成 `[?]`
8. 以 changelog 章節作結

`[SPEC]` 的內容規則：
- 優先用條列，不要用散文
- 多欄位的事實優先用表格
- 語法、格式、範例優先用程式碼區塊
- 散文最多 2 句，需要更多就移到 `[NOTE]`

`[BUG]` 的內容規則：
- 一定要包含：symptom、cause、fix
- 選填：受影響的版本、workaround
- 標題寫在同一行：`**[BUG] Short description**`

**[NOTE]**
把既有文件轉成 HADS 時：把事實抽出來放進 `[SPEC]`，把敘述和歷史移到 `[NOTE]`，把所有已知的問題浮現成 `[BUG]`。不要在不同的區塊類型之間重複內容。

---

## 6. 驗證規則

**[SPEC]**
一份有效的 HADS 文件必須有：
- H1 標題
- 前 20 行內有 `**Version X.Y.Z**`
- 在第一個內容章節之前有 AI manifest
- 所有區塊標籤都要粗體：是 `**[SPEC]**`，不是 `[SPEC]`，也不是 *[SPEC]*
- `[BUG]` 區塊至少包含 symptom + fix

Validator：*（已規劃，這個版本尚未包含）*

---

## 7. 互動範例

**[SPEC]**

使用者：*"Write HADS documentation for this REST API"*
→ 產生完整的 HADS 文件：header、manifest、帶有 [SPEC]/[NOTE]/[BUG] 區塊的章節

使用者：*"Convert this README to HADS format"*
→ 把既有內容重組成 HADS 區塊，保留所有事實，並加上 manifest

使用者：*"Is this document valid HADS?"*
→ 檢查：H1 標題、版本、manifest、區塊標籤格式、BUG 區塊是否完整

使用者：*"Summarize this HADS document"*
→ 只讀 [SPEC] 和 [BUG] 區塊，回傳結構化的摘要

使用者：*"What does this API do?"*（有提供 HADS 文件）
→ 讀 manifest，讀相關章節中的 [SPEC] 區塊，直接回答

---

## 8. 設計意圖

**[NOTE]**
HADS 之所以存在，是因為 AI 模型越來越常比人類更早讀到文件。這個格式針對這個現實做最佳化，同時不犧牲人類的可讀性。

關鍵洞察：AI manifest 是核心創新。它讓連小型（7B）模型都知道什麼該讀、什麼該跳過，不需要它們去推理文件結構。對模型來說，明確比隱含更好。

產生 HADS 的時候，把 `[SPEC]` 想成 API 介面，把 `[NOTE]` 想成註解。`[BUG]` 區塊是最有價值的內容，它們代表來之不易的知識，能讓別人不必撞上同一堵牆。

---

## 9. 快速參考

**[SPEC]**
```
Tag       | 粗體格式       | 讀者    | 必要內容
----------|----------------|---------|------------------
[SPEC]    | **[SPEC]**     | AI      | 事實，精簡
[NOTE]    | **[NOTE]**     | 人類    | 脈絡、敘述
[BUG]     | **[BUG] ...**  | 兩者    | Symptom + fix
[?]       | **[?]**        | 兩者    | 未驗證的主張
```

Manifest 最低要求：
```markdown
## AI READING INSTRUCTION
Read `[SPEC]` and `[BUG]` blocks for authoritative facts.
Read `[NOTE]` only if additional context is needed.
`[?]` blocks are unverified.
```
