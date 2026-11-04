---
name: distilly
description: "設定 owner profile，讓個人 agent 知道自己在幫誰做事（第一次設定、「認識我」），或把同事、人際關係、名人的素材蒸餾成可重複使用的 Person Profile 給 agent 用。"
argument-hint: "[character] [name-or-slug]"
version: "1.0.0"
user-invocable: true
allowed-tools: Read, Write, Edit, Bash
---

> **語言**：這些指令是用英文寫的。從使用者的第一則訊息判斷他用什麼語言，之後全程用那個語言回覆。

> **Skill Root**：讀取內附的 prompt 或執行內附的 script 之前，先解析出 host 實際載入的那個 `SKILL.md` 所在的絕對目錄。下面的指令裡，`{distilly_skill_root}` 就是指那個目錄。Claude Code 把它暴露成 `${CLAUDE_SKILL_DIR}`；其他 host 就用它的探索 context 提供的已載入 skill 路徑。不要假設 shell 目前的工作目錄就是 Skill root，也不要猜或寫死安裝路徑。如果 host 沒有暴露載入路徑，或有多個 Distilly 安裝而無法判斷，就先請使用者指出正在用的是哪一個，再執行程式。
>
> shell 要停在使用者目前的 workspace，這樣像 `./skills/...` 這種相對輸出路徑才會留在專案內。每個 `tools/...` 和 `prompts/...` 資源都要以 `{distilly_skill_root}` 為基準解析。例如，要執行 `tools/owner_profile.py`，就寫成 `python3 "{distilly_skill_root}/tools/owner_profile.py"`；實際呼叫工具時，要把 placeholder 換成解析後的絕對路徑。

# Distilly Creator

> Distilly 以前叫 **Colleague Skill / colleague-skill**。現在 Skill 的 frontmatter name 和 creator 入口都是 `distilly`。

## 判斷請求要走哪條流程

只讀這個請求需要的那個 flow 檔，然後照著做。

| 使用者說 | Flow |
|---------------|------|
| 「Set up my profile」/「Get to know me」/「Who am I to you」、「distill myself」，或 host 第一次執行、還沒有 owner profile | `prompts/flows/owner.md` |
| `/distilly`、「Help me create a skill」、「Create a new skill」、「I want to distill someone」、「Make a skill for XX」 | `prompts/flows/create.md`（它的 Step 0 會把 `owner` 送回 owner flow） |
| 「I have new files」/「append」、「That's wrong」/「He wouldn't do that」/「He should be」、`/update-skill {character} {slug}`，或別名 `/update-colleague {slug}` | `prompts/flows/evolve.md` |
| 「Show my skills」、回滾或刪除已產生的 skill | `prompts/flows/manage.md` |

create flow 會引入 `prompts/flows/sources.md` 來匯入素材，如果是 `celebrity`，還會引入 `prompts/flows/celebrity_research.md`。每個 flow 都會列出它需要的 prompt；等 flow 走到那一步再讀，不要一開始就全部讀。

## 每個 flow 都要遵守的規則

- **儲存位置**：產生的 skill 放在使用者 workspace 裡的 `./skills/colleague/{slug}/`、`./skills/relationship/{slug}/` 或 `./skills/celebrity/{slug}/`。要放全域路徑的話，用 `--base-dir` 傳入該類別的儲存根目錄。
- **寫入**：產生的 skill 只能透過 `tools/skill_writer.py` 建立和更新；絕對不要手動建構或手動編輯它們的檔案。
- **憑證**：App Secret、access 或 refresh token、Bot Token 和 OAuth code 絕對不能進到對話裡。不要跟使用者要這些；使用者要在自己的終端機執行 collector 的 `--setup` / `--login`。細節看 `prompts/flows/sources.md`。

## 相容的 host

Claude Code、OpenClaw、Hermes、Codex、DeepSeek Harness、Pi coding agent、Grok Build 和 OpenCode。在 Claude Code、Hermes、DeepSeek Harness 和 Grok Build 用 `/distilly` 呼叫；OpenClaw 用 `/distilly` 或 `/skill distilly`；Codex 用 `$distilly` 或 `/skills`；Pi 用 `/skill:distilly`。OpenCode 原生載入 Skill，沒有專屬指令。Grok Bot 無法直接匯入這個目錄；不要把這個 repo 說成是 Grok Bot 的安裝方式。
