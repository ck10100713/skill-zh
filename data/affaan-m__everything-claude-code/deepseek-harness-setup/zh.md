---
name: deepseek-harness-setup
description: "在 DeepSeek Harness（DSH）上安裝並操作 Everything Claude Code（ECC）：原生 skill 根目錄（~/.dsh/skills、.agents/skills）、用於 command hook 的 @deepseek-ai/dsh-hooks-claude-code 橋接器、bare-insert 的 patch 掛載、generator 的用法、事件支援的限制，以及更新流程。當要在 DeepSeek Harness 上設定 ECC、把 ECC hook 接進 DSH profile，或除錯為什麼 ECC 的 skill 或 hook 沒有出現在 DSH session 裡時使用。"
metadata:
  origin: community
---

# DeepSeek Harness 設定

在 DeepSeek Harness 上跑 ECC。完整指南：`docs/DEEPSEEK-HARNESS-GUIDE.md`。

## 何時使用

- 在 DeepSeek Harness 的安裝上安裝 ECC 的 skill 或 hook。
- 判斷哪些 ECC 功能在 DSH 上能用、哪些不能。
- 除錯一個沒有顯示 ECC skill、或沒有觸發 ECC hook 的 DSH session。

## 運作方式

1. **Skill 不需要轉換。** DSH 會從原生的 skill 根目錄讀取 `SKILL.md` 的 frontmatter（name/description）。把 ECC 的目錄連結過去一次就好：

   ```bash
   ln -s /path/to/ECC/skills/<skill-name> ~/.dsh/skills/<skill-name>
   ```

   根目錄的優先順序（專案的 `.dsh` 和 `.agents` 根目錄優先於 `~/.dsh`）：如果名稱已經存在於優先順序更高的根目錄，就跳過不連結。把佔位符換成真正的 skill 名稱；角括號不是 shell 語法。

2. **Hook 要透過官方的橋接器。** 從標準的 ECC hooks 檔案產生 DSH 格式的設定：

   ```bash
   node scripts/dsh/generate-hooks-config.js --ecc-root /path/to/ECC --out ~/.dsh/ecc/hooks-dsh.json
   ```

   generator 會把工具名稱的 matcher 轉成小寫、把 `CLAUDE_PLUGIN_ROOT`/`ECC_PLUGIN_ROOT` 以行內方式加到前面（橋接器不會匯出 plugin 根目錄）、保留 timeout，並跳過 DSH 沒辦法橋接的事件：`PreCompact`、`PostToolUseFailure`、`SessionEnd`。

3. **用 bare insert 掛載**，寫在 `~/.dsh/profiles/<profile>/cordis.patch.yml`：

   ```yaml
   - insert:
       - id: ecc-hooks-claude-code
         name: "@deepseek-ai/dsh-hooks-claude-code"
         config:
           configPath: /absolute/path/to/hooks-dsh.json
   ```

   這些 loader 的規則是吃過虧才學到、很花除錯時間的：頂層單純的 `- id:` 項目會被默默丟掉；對既有的非群組 id 做 `insert` 會被以「not a group」拒絕；官方的 plugin 套件不需要在 profile 的 `package.json` 裡加項目。

4. **先組合驗證，再即時確認。**

   ```bash
   cd ~/.dsh && dsh --profile web --dump-config > /tmp/dump.yml
   grep ecc-hooks /tmp/dump.yml
   ```

   即使 loader 丟掉或拒絕了某個項目，組合的結束狀態碼還是 0，這些問題只會報在 stderr。要確認項目的 id 有出現在 dump 裡，而且 stderr 是空的。session 第一次 edit/write/bash 時看到 GateGuard 的即時拒絕，就是橋接器已經啟用的明確訊號。

## 更新

`git pull` 會立刻反映到已連結的 skill；hooks 設定要用同一個 generator 指令重新產生。如果 ECC 的 checkout 搬了位置，要重新產生（路徑被嵌在每個 hook 指令裡），並重新連結 skill。

## 限制

| 功能 | 在 DSH 上的狀態 |
|---------|---------------|
| Skills | 原生探索；workflow 可能需要針對 host 調整 |
| Hooks | 7 個橋接事件中的 5 個，共 23 個 command hook |
| Slash commands | 不可用（這是 Claude Code 的機制）；workflow 由 skill 涵蓋 |
| Agents | 原生派送尚未驗證；審查之後才使用標準的 prompt 指引 |

這裡驗證過的設定針對的是 CLI/web profile。桌面版 profile 有獨立、由安裝擁有的 runtime，skill 的探索必須在那邊另外驗證。
只從審查過的 ECC checkout 產生 hook；被連結的 checkout 提供它們的 runtime。
