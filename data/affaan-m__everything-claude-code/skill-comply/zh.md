---
name: skill-comply
description: 視覺化呈現 skill、規則和 agent 定義到底有沒有被遵守：自動產生 3 種 prompt 嚴格程度的情境、執行 agent、將行為序列分類，並回報帶有完整 tool call 時間軸的遵守率。想檢查 agent 是否真的遵循被給予的 skill、規則和定義，而不是假設它們有遵守時使用。
metadata:
  origin: ECC
tools: Read, Bash
---

# skill-comply：自動化遵守度量測

衡量 coding agent 是否真的遵循 skill、規則或 agent 定義，做法是：
1. 從任何 .md 檔自動產生預期的行為序列（規格）
2. 自動產生 prompt 嚴格程度遞減的情境（支持 → 中立 → 對立）
3. 執行 `claude -p`，並透過 stream-json 擷取 tool call 軌跡
4. 用 LLM（不是 regex）把 tool call 對照規格步驟分類
5. 以確定性的方式檢查時間先後順序
6. 產生獨立完整的報告，包含規格、prompt 和時間軸

## 支援的目標

- **Skill**（`skills/*/SKILL.md`）：像 search-first、TDD 指南這類工作流程 skill
- **規則**（`rules/common/*.md`）：像 testing.md、security.md、git-workflow.md 這類強制規則
- **Agent 定義**（`agents/*.md`）：檢查 agent 在預期時機有沒有被呼叫（尚不支援驗證內部工作流程）

## 何時啟用

- 使用者執行 `/skill-comply <path>`
- 使用者問「這條規則真的有被遵守嗎？」
- 新增規則/skill 之後，驗證 agent 的遵守度
- 作為品質維護的一部分，定期執行

## 使用方式

```bash
# Full run
uv run python -m scripts.run ~/.claude/rules/common/testing.md

# Dry run (no cost, spec + scenarios only)
uv run python -m scripts.run --dry-run ~/.claude/skills/search-first/SKILL.md

# Custom models
uv run python -m scripts.run --gen-model haiku --model sonnet <path>
```

## 關鍵概念：Prompt 獨立性

衡量即使 prompt 沒有明確支持，skill/規則是否仍被遵守。

## 報告內容

報告是獨立完整的，包含：
1. 預期的行為序列（自動產生的規格）
2. 情境 prompt（每個嚴格程度下問了什麼）
3. 每個情境的遵守分數
4. 帶有 LLM 分類標籤的 tool call 時間軸

### 進階（選用）

熟悉 hook 的使用者，報告還會針對遵守度低的步驟，附上 hook 升級建議。這只是參考資訊，主要價值是遵守度本身的可見性。
