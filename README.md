# Skill 寫法圖鑑

收集知名人士寫的 Claude Code skill。每頁先放中文翻譯，再放英文原文，方便對照學寫法。

網站：https://ck10100713.github.io/skill-zh/

| 作者 | 來源 | 授權 |
|---|---|---|
| Matt Pocock | [mattpocock/skills](https://github.com/mattpocock/skills) | MIT |
| Garry Tan | [garrytan/gstack](https://github.com/garrytan/gstack) | MIT |
| Anthropic | [anthropics/skills](https://github.com/anthropics/skills) | Apache-2.0 |
| Cloudflare | [cloudflare/skills](https://github.com/cloudflare/skills) | Apache-2.0 |
| Jesse Vincent | [obra/superpowers](https://github.com/obra/superpowers) | MIT |

新增 skill：在 `data/<owner>__<repo>/<skill>/` 放 `en.md`（英文原文）、`zh.md`（中文）、`meta.json`，然後跑 `python3 build.py` 重新產生網站。分類清單在 `build.py` 的 `CATEGORIES`。

## 授權

原文版權屬各原作者，依原 repo 授權收錄，每頁都附原文連結。中文為本 repo 翻譯，屬於對原文的修改。Apache-2.0 授權全文見 [LICENSES/Apache-2.0.txt](LICENSES/Apache-2.0.txt)。Anthropic 的 docx、pdf、pptx、xlsx 四份是 source-available 授權，不開放轉載，所以沒有收錄。
