---
name: using-superpowers
description: 開始任何對話時使用：建立怎麼找 skill、怎麼用 skill 的規矩，要求在任何回應之前（包括釐清用的問題）先呼叫 skill
---

<SUBAGENT-STOP>
如果你是被派出去執行特定任務的 subagent，忽略這個 skill。
</SUBAGENT-STOP>

<EXTREMELY-IMPORTANT>
只要你覺得某個 skill 有哪怕 1% 的機會適用於你正在做的事，你就絕對一定要呼叫那個 skill。

如果有 SKILL 適用於你的任務，你沒有選擇。你一定要用它。

這沒得談。你沒辦法靠合理化脫身。
</EXTREMELY-IMPORTANT>

## 規則

**在任何回應或動作「之前」，先呼叫相關或被要求的 skill**，包括釐清用的問題、探索程式碼庫，或檢查檔案。如果結果發現它不適合這個情況，你也不一定要用它。

**進入 plan mode 之前：** 如果你還沒 brainstorm 過，先呼叫 brainstorming skill。

然後宣告「Using [skill] to [purpose]」，並完全照著 skill 做。如果它有檢查表，每一項建立一個 todo。

## Skill 優先順序

當有多個 skill 適用時，流程型 skill 優先：它們定下做法，然後由實作型 skill（frontend-design 等）執行。Brainstorming 和 systematic-debugging 是 Superpowers 最常見的流程型 skill，但這條規則適用於其中任何一個。

- 「Let's build X」→ 先用 superpowers:brainstorming，再用實作型 skill。
- 「Fix this bug」→ 先用 superpowers:systematic-debugging，再用領域型 skill。

## 警訊

這些想法表示停下來，你正在合理化：

| 想法 | 現實 |
|---------|---------|
| 「這只是個簡單的問題」 | 問題也是任務。檢查有沒有 skill。 |
| 「我需要先有更多 context」 | 檢查 skill 在釐清問題「之前」。 |
| 「我先探索一下程式碼庫」 | Skill 告訴你「怎麼」探索。先檢查。 |
| 「我可以很快看一下 git／檔案」 | 檔案缺少對話的 context。檢查有沒有 skill。 |
| 「我先收集一些資訊」 | Skill 告訴你「怎麼」收集資訊。 |
| 「這不需要正式的 skill」 | 如果有 skill，就用它。 |
| 「我記得這個 skill」 | Skill 會演進。讀目前的版本。 |
| 「這不算任務」 | 行動 = 任務。檢查有沒有 skill。 |
| 「這個 skill 太殺雞用牛刀了」 | 簡單的事會變複雜。用它。 |
| 「我先做這一件事就好」 | 在做任何事「之前」就檢查。 |
| 「這樣感覺很有產出」 | 沒有紀律的行動浪費時間。Skill 能預防這種事。 |
| 「我知道那是什麼意思」 | 知道概念 ≠ 使用 skill。呼叫它。 |

## 平台適配

如果你的 harness 出現在這裡，讀它的參考檔，了解特別的指示：

- Claude Code：`references/claude-code-tools.md`
- Codex：`references/codex-tools.md`
- Pi：`references/pi-tools.md`
- Antigravity：`references/antigravity-tools.md`
- Hermes Agent：`references/hermes-tools.md`
- Muse：`references/muse-tools.md`

## 使用者指示

使用者的指示（CLAUDE.md、AGENTS.md、GEMINI.md 等，以及直接的請求）優先於 skill，而 skill 又優先於預設行為。只有在你的搭檔明確叫你這麼做時，才跳過 skill 的工作流程或指示。
