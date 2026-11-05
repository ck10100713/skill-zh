# Skill 寫法圖鑑

收集各家 Claude Code skill。每頁先放中文翻譯，再放英文原文，方便對照學寫法。

網站：https://skill.pochenkuo.com/

<!-- sources:start -->
| 作者 | 來源 | 授權 | 份數 |
|---|---|---|---|
| affaan-m | [affaan-m/everything-claude-code](https://github.com/affaan-m/everything-claude-code) | MIT | 316 |
| asgard-ai-platform | [asgard-ai-platform/skills](https://github.com/asgard-ai-platform/skills) | MIT | 314 |
| Anthropic | [anthropics/knowledge-work-plugins](https://github.com/anthropics/knowledge-work-plugins) | Apache-2.0 | 232 |
| Microsoft | [microsoft/skills](https://github.com/microsoft/skills) | MIT | 211 |
| wshobson | [wshobson/agents](https://github.com/wshobson/agents) | MIT | 185 |
| Donchitos | [Donchitos/Claude-Code-Game-Studios](https://github.com/Donchitos/Claude-Code-Game-Studios) | MIT | 74 |
| Anthropic | [anthropics/financial-services](https://github.com/anthropics/financial-services) | Apache-2.0 | 64 |
| jezweb | [jezweb/claude-skills](https://github.com/jezweb/claude-skills) | MIT | 63 |
| Garry Tan | [garrytan/gstack](https://github.com/garrytan/gstack) | MIT | 41 |
| Matt Pocock | [mattpocock/skills](https://github.com/mattpocock/skills) | MIT | 35 |
| AgriciDaniel | [AgriciDaniel/claude-ads](https://github.com/AgriciDaniel/claude-ads) | MIT | 34 |
| AgriciDaniel | [AgriciDaniel/claude-seo](https://github.com/AgriciDaniel/claude-seo) | MIT | 33 |
| KerberosClaw | [KerberosClaw/kc_ai_skills](https://github.com/KerberosClaw/kc_ai_skills) | MIT | 26 |
| alchaincyf | [alchaincyf/nuwa-skill](https://github.com/alchaincyf/nuwa-skill) | MIT | 16 |
| Anthropic | [anthropics/skills](https://github.com/anthropics/skills) | Apache-2.0 | 15 |
| Jesse Vincent | [obra/superpowers](https://github.com/obra/superpowers) | MIT | 15 |
| Cloudflare | [cloudflare/skills](https://github.com/cloudflare/skills) | Apache-2.0 | 11 |
| MadsLorentzen | [MadsLorentzen/ai-job-search](https://github.com/MadsLorentzen/ai-job-search) | MIT | 9 |
| HumanLayer | [humanlayer/skills](https://github.com/humanlayer/skills) | MIT | 7 |
| nextlevelbuilder | [nextlevelbuilder/ui-ux-pro-max-skill](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill) | MIT | 7 |
| DietrichGebert | [DietrichGebert/ponytail](https://github.com/DietrichGebert/ponytail) | MIT | 6 |
| KKKKhazix | [KKKKhazix/khazix-skills](https://github.com/KKKKhazix/khazix-skills) | MIT | 6 |
| zz41354899 | [zz41354899/open-slidex](https://github.com/zz41354899/open-slidex) | MIT | 6 |
| Hao0321 | [Hao0321/claude-skill-social-post](https://github.com/Hao0321/claude-skill-social-post) | MIT | 2 |
| WalterSumbon | [WalterSumbon/claude-agent-sdk-skill](https://github.com/WalterSumbon/claude-agent-sdk-skill) | Apache-2.0 | 2 |
| Microsoft | [microsoft/SkillOpt](https://github.com/microsoft/SkillOpt) | MIT | 2 |
| Kappaemme-git | [Kappaemme-git/codex-complexity-optimizer](https://github.com/Kappaemme-git/codex-complexity-optimizer) | MIT | 1 |
| Alibaba FlyAI | [alibaba-flyai/flyai-skill](https://github.com/alibaba-flyai/flyai-skill) | MIT | 1 |
| ayghri | [ayghri/i-have-adhd](https://github.com/ayghri/i-have-adhd) | MIT | 1 |
| cathrynlavery | [cathrynlavery/diagram-design](https://github.com/cathrynlavery/diagram-design) | MIT | 1 |
| chuspeeism | [chuspeeism/dashi-ppt-skill](https://github.com/chuspeeism/dashi-ppt-skill) | AGPL-3.0 | 1 |
| drpwchen | [drpwchen/lecture-to-notes](https://github.com/drpwchen/lecture-to-notes) | MIT | 1 |
| eternity4719 | [eternity4719/HowToLiveBetter](https://github.com/eternity4719/HowToLiveBetter) | CC-BY-4.0 | 1 |
| Goldman Sachs | [goldmansachs/gs-quant](https://github.com/goldmansachs/gs-quant) | Apache-2.0 | 1 |
| mars-tw | [mars-tw/open-seo-advisor-skill](https://github.com/mars-tw/open-seo-advisor-skill) | Apache-2.0 | 1 |
| santifer | [santifer/career-ops](https://github.com/santifer/career-ops) | MIT | 1 |
| teng-lin | [teng-lin/notebooklm-py](https://github.com/teng-lin/notebooklm-py) | MIT | 1 |
| titanwings | [titanwings/colleague-skill](https://github.com/titanwings/colleague-skill) | MIT | 1 |
| truongduy2611 | [truongduy2611/app-store-preflight-skills](https://github.com/truongduy2611/app-store-preflight-skills) | MIT | 1 |
| Uncle Bob | [unclebob/ub-mode](https://github.com/unclebob/ub-mode) | MIT | 1 |
| virgiliojr94 | [virgiliojr94/book-to-skill](https://github.com/virgiliojr94/book-to-skill) | MIT | 1 |
| yazelin | [yazelin/slide-deck-skill](https://github.com/yazelin/slide-deck-skill) | MIT | 1 |
<!-- sources:end -->

新增 skill：在 `data/<owner>__<repo>/<skill>/` 放 `en.md`（英文原文）、`zh.md`（中文）、`meta.json`，然後跑 `python3 build.py` 重新產生網站。分類清單在 `build.py` 的 `CATEGORIES`。

## 授權

原文版權屬各原作者，依原 repo 授權收錄，每頁都附原文連結。中文為本 repo 翻譯，屬於對原文的修改。Apache-2.0 授權全文見 [LICENSES/Apache-2.0.txt](LICENSES/Apache-2.0.txt)。各 repo 的授權見上表；dashi-ppt-skill 為 AGPL-3.0、HowToLiveBetter 為 CC-BY-4.0，衍生內容沿用同一授權。沒附授權的 repo 不收錄。Anthropic 的 docx、pdf、pptx、xlsx 四份是 source-available 授權，不開放轉載，所以沒有收錄。
