---
name: m365-agent-evaluator
description: >
  使用者想用公開的 @microsoft/m365-copilot-eval CLI，建立、執行或分析 Microsoft 365 Copilot declarative agent 的評估套件時，用這個 skill。出現這類意圖時觸發："evaluate my agent"、"test my agent"、"run my evals"、"create eval prompts"、"add multi-turn tests"、"tune evaluator thresholds"、"why is my agent failing"，或 "set up eval environment variables"。
---

# M365 Agent Evaluator

用這個 skill 協助使用者以 `@microsoft/m365-copilot-eval` 評估 Microsoft 365 Copilot declarative agent。這個 skill 會設計符合 schema 的 eval 資料集、執行公開 preview 版的 CLI、分析結果，並建議有針對性的修正。

偵測到 Microsoft 365 Agents Toolkit (ATK) 專案時，預設以 ATK 專案處理，但不要只因為目前目錄不是 ATK 就直接停手。CLI 也可以搭配明確的 `M365_AGENT_ID` 或 `--m365-agent-id` 來評估已部署的 agent。

## Always use this CLI invocation

```powershell
npx -y --package @microsoft/m365-copilot-eval@latest runevals
```

不要推薦舊的私有 `aka.ms` 安裝程式、全域安裝、單純的 `runevals`、單純的 `npx runevals`、`--input` 或 `--html`。

## Activation workflow

1. 找出使用者的目標：設定、撰寫資料集、執行 eval、分析結果，或更新現有的 eval 套件。
2. 只載入當前目標需要的 reference：
   - `references/workflow.md`：端到端的操作流程和 CLI 指令。
   - `references/azure-setup.md`：前置需求、env 檔案和 secret 處理。
   - `references/eval-templates.md`：建立或編輯 eval 資料集時。
   - `references/pra-framework.md`：決定要產生哪些情境時。
   - `references/result-analysis.md`：JSON/CSV/HTML 結果出來之後。
   - `references/guardrails.md`：寫檔案、處理 secret、清除快取、登出或疑難排解之前。
3. 偵測專案型態：
   - ATK：`.env.local`、`.env.local.user`、`env\.env.local.user`、`m365agents.yml` 或 `appPackage\declarativeAgent.json`。
   - 非 ATK：一份 eval 資料集，加上 `M365_AGENT_ID`、`--m365-agent-id`，或具名的環境檔，例如 `env\.env.dev`。
4. 驗證前置需求，但不要洩漏值：
   - Node.js 24.12.0 或更新版本。
   - Microsoft 365 Copilot 授權，以及已部署的 M365 Copilot agent。
   - WorkIQ Client App 的 tenant admin consent。
   - `TENANT_ID`、Azure OpenAI in Foundry Models 的 endpoint/key，以及建議/預設的 `gpt-4o-mini` deployment。
5. 選擇工作流程：
   - 沒有資料集：建立 `evals\evals.json`。
   - 已有資料集：執行、分析先前的結果，或提出修改建議。
   - 快速檢查：用 inline prompt。
   - 探索：用互動模式。

## Current dataset contract

產生 schema 版本 `1.2.0` 的文件，根層級是 `items` 陣列。不要產生舊的 `PromptsObject` 或根層級 `prompts` 格式。

最小結構：

```json
{
  "schemaVersion": "1.2.0",
  "metadata": {
    "name": "Agent evaluation suite",
    "tags": ["starter"]
  },
  "default_evaluators": {
    "Relevance": {},
    "Coherence": {}
  },
  "items": [
    {
      "prompt": "What can this agent help me with?",
      "expected_response": "The agent explains its supported scope without inventing unsupported capabilities."
    }
  ]
}
```

本機的 schema 來源用 `references\prompts-schema.json`，可直接複製的單輪、多輪、evaluator 和門檻範例見 `references\eval-templates.md`。

## Public evaluator names

Evaluator 名稱區分大小寫。除非有更新的權威來源證明不同，否則只用公開可設定的 evaluator 名稱。

| Evaluator | Semantics |
|---|---|
| `Relevance` | LLM 評分 1-5；預設門檻 3。 |
| `Coherence` | LLM 評分 1-5；預設門檻 3。 |
| `Groundedness` | 依 `context`/預期證據，LLM 評分 1-5；預設門檻 3。 |
| `Similarity` | 依 `expected_response`，LLM 評分 1-5；預設門檻 3。 |
| `Citations` | 以數量為基礎的引用檢查；預設門檻 1。 |
| `ExactMatch` | 布林值，字串完全相符。 |
| `PartialMatch` | 字串相似度 0.0-1.0；預設門檻 0.5。 |

撰寫資料集時，把 `ToolCallAccuracy` 視為舊版/私有。除非目前公開的 CLI/schema 文件明確重新引入，否則不要把它加進產生的資料集。

## Common commands

```powershell
# Version/help checks
npx -y --package @microsoft/m365-copilot-eval@latest runevals --version
npx -y --package @microsoft/m365-copilot-eval@latest runevals --help

# First-time setup / EULA
npx -y --package @microsoft/m365-copilot-eval@latest runevals accept-eula
npx -y --package @microsoft/m365-copilot-eval@latest runevals --init-only

# Batch run with explicit JSON output
npx -y --package @microsoft/m365-copilot-eval@latest runevals --prompts-file evals\evals.json --output .evals\results.json

# Human-review HTML or spreadsheet-friendly CSV
npx -y --package @microsoft/m365-copilot-eval@latest runevals --prompts-file evals\evals.json --output .evals\results.html
npx -y --package @microsoft/m365-copilot-eval@latest runevals --prompts-file evals\evals.json --output .evals\results.csv

# Quick checks
npx -y --package @microsoft/m365-copilot-eval@latest runevals --prompts "What can you help me with?" --expected "The agent describes its supported scope."

# Non-ATK or named environment
npx -y --package @microsoft/m365-copilot-eval@latest runevals --prompts-file evals\evals.json --m365-agent-id <agent-id> --env dev
```

`--concurrency` 只能用 1-5 的值。除錯時從 `1` 開始，設定穩定之後才往上加。

## Version and PATH safety

在診斷 agent 的行為之前，先確認正在執行的是哪個執行檔：

```powershell
Get-Command runevals -All
npm list -g @microsoft/m365-copilot-eval --depth=0
npm view @microsoft/m365-copilot-eval version
npx -y --package @microsoft/m365-copilot-eval@latest runevals --version
npx -y --package @microsoft/m365-copilot-eval@latest where runevals
```

如果單純的 `runevals` 印出 `This version of the M365 Evals CLI has stopped working and must be updated`，就把它當成過期的 PATH/全域安裝問題。用上面的 `npx --package ...@latest` 指令重新執行，然後先問過使用者，才用 `npm uninstall -g @microsoft/m365-copilot-eval` 移除全域 shim。

## File conventions

| Path | Purpose |
|---|---|
| `.env.local` | 非機密的 ATK 設定，例如 `M365_TITLE_ID`。 |
| `.env.local.user` 或 `env\.env.local.user` | 本機機密，例如 tenant ID 和 Azure OpenAI key。 |
| `env\.env.<environment>` | 非 ATK 或明確使用 `--env` 流程的具名環境設定。 |
| `evals\evals.json` | 使用者想 commit 的話，放進版控的 eval 資料集。 |
| `.evals\` | 本機的執行輸出；通常會 gitignore。 |

絕對不要印出或 commit 機密、含敏感資料的 prompt、取回的內容、debug log 或原始結果檔，除非使用者明確要求，並確認這些資料可以安全分享。

## Generation guidance

把 PRA 當作設計情境的框架：

- Perceive：檢索、grounding 和來源涵蓋範圍。
- Reason：遵守 instructions、綜合整理、處理模糊情況和拒答行為。
- Act：已宣告的 capability/action 行為。用公開的 evaluator 來評分，例如 `Relevance`、`Coherence`、`Similarity`、`ExactMatch` 或 `PartialMatch`；不要用舊版的 `ToolCallAccuracy`。

覆寫既有資料集之前要先問。寫入產生的 eval 時，先寫到暫存檔，成功後再重新命名。

## Result analysis guidance

只分析實際存在的 evaluator key。缺少分數的 key，通常代表那個項目沒有設定該 evaluator，不代表它失敗了。

有的話用目前的分數 key：`relevance`、`coherence`、`groundedness`、`similarity`、`citations`、`exactMatch` 和 `partialMatch`。把失敗歸類到可能的根本原因：instruction 問題、grounding 問題、引用問題、預期答案不一致、capability 缺口、auth/環境問題，或 eval 品質問題。

除非使用者已經提供或核准必要的 tenant、agent 和 Azure OpenAI 設定，否則不要執行依賴真實 tenant 的 eval。
