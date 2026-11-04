---
name: discover-azure-skills
description: "搜尋 Azure skill 目錄，把 Azure 任務對應到 skill 的 metadata 和 plugin 安裝指引，推薦可安裝的 agent skill。WHEN: 在開始任何涉及 Azure 或 Microsoft 雲端服務、產品或資料來源的任務之前，而且目前載入的 skill 或工具都還沒涵蓋它時。"
license: MIT
metadata:
  author: Microsoft
  version: "1.0.2"
---

照這些步驟，找出符合任務描述的 Azure skill。

1. 列出 plugin

從 GitHub Contents API 列出 Azure plugin 目錄：https://api.github.com/repos/microsoft/azure-skills/contents/.github/plugins?ref=main

結果中每個 `type` 是 `dir` 的項目就是一個 plugin 目錄。Skill 是按 plugin 來組織的。

2. 列出 skill

對每個 plugin，從 GitHub Contents API 列出它的 skill：https://api.github.com/repos/microsoft/azure-skills/contents/.github/plugins/{plugin-dirname}/skills?ref=main

結果中每個 `type` 是 `dir` 的項目就是一個 skill 目錄。每個 skill 都有一份 SKILL.md，說明這個 skill 該用在什麼地方。

3. 找出相關的 skill

先從名稱剔除明顯不相關的 skill。剩下的每一個，從 API 讀它們的 description：https://raw.githubusercontent.com/microsoft/azure-skills/main/.github/plugins/{plugin-dirname}/skills/{skill-name}/SKILL.md

再用 description 進一步剔除不相關的 skill。

4. 找出相關 skill 所屬的 plugin 名稱

對每個相關的 skill，從 GitHub Contents API 讀取 `plugin.json` 來找出它的 plugin 名稱：https://raw.githubusercontent.com/microsoft/azure-skills/main/.github/plugins/{plugin-dirname}/.plugin/plugin.json

這點很重要，因為 plugin 的名稱可能和它的目錄名稱不同。安裝指令要用的是 plugin 名稱。

5. 回報比對到的 skill

回報比對到的 skill，並提供安裝說明。Skill 是透過安裝它的 plugin 來安裝的。讀取對應 agent client 的安裝說明，再提供給使用者。

- [Copilot CLI](./references/install/copilot-cli.md)
- [Claude Code](./references/install/claude-code.md)
- [Other](./references/install/other.md)
