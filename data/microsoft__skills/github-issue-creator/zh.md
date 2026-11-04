---
name: github-issue-creator
description: 把原始筆記、錯誤 log、語音口述或截圖，轉換成簡潔的 GitHub-flavored markdown issue 報告。使用者貼上 bug 資訊、錯誤訊息或隨口的描述，想要結構化的 GitHub issue 時使用。支援用圖片/GIF 當視覺證據。
---

# GitHub Issue Creator

把雜亂的輸入（錯誤 log、語音筆記、截圖）轉成乾淨、可以行動的 GitHub issue。

## Output Template

```markdown
## Summary
[One-line description of the issue]

## Environment
- **Product/Service**: 
- **Region/Version**: 
- **Browser/OS**: (if relevant)

## Reproduction Steps
1. [Step]
2. [Step]
3. [Step]

## Expected Behavior
[What should happen]

## Actual Behavior
[What actually happens]

## Error Details
```
[Error message/code if applicable]
```

## Visual Evidence
[Reference to attached screenshots/GIFs]

## Impact
[Severity: Critical/High/Medium/Low + brief explanation]

## Additional Context
[Any other relevant details]
```

## Output Location

**把 issue 建成 markdown 檔案**，放在 repo 根目錄的 `/issues/` 目錄。命名慣例：`YYYY-MM-DD-short-description.md`

## Guidelines

**要簡潔**：不講廢話。每個字都要有價值。

**從混亂中抽出結構**：語音口述和原始筆記常常把事實埋在口語裡。把它們挖出來。

**推斷缺少的 context**：如果使用者提到「同一個專案」或「那個 dashboard」，就用對話或記憶裡的 context 補上具體資訊。

**敏感資料用佔位符**：任何可能敏感的東西，用 `[PROJECT_NAME]`、`[USER_ID]` 等佔位符。

**嚴重程度要符合影響**：
- Critical：服務掛了、資料遺失、安全問題
- High：主要功能壞了，沒有 workaround
- Medium：功能受損，但有 workaround
- Low：小小的不便、外觀問題

**圖片/GIF 處理**：直接 inline 引用附件。格式：`![Description](attachment-name.png)`

## Examples

**Input (voice dictation)**:
> so I was trying to deploy the agent and it just failed silently no error nothing the workflow ran but then poof gone from the list had to refresh and try again three times

**Output**:
```markdown
## Summary
Agent deployment fails silently - no error displayed, agent disappears from list

## Environment
- **Product/Service**: Azure AI Foundry
- **Region/Version**: westus2

## Reproduction Steps
1. Navigate to agent deployment
2. Configure and deploy agent
3. Observe workflow completes
4. Check agent list

## Expected Behavior
Agent appears in list with deployment status, errors shown if deployment fails

## Actual Behavior
Agent disappears from list. No error message. Requires page refresh and retry.

## Impact
**High** - Blocks agent deployment workflow, no feedback on failure cause

## Additional Context
Required 3 retry attempts before successful deployment
```

---

**Input (error paste)**:
> Error: PERMISSION_DENIED when publishing to Teams channel. Code: 403. Was working yesterday.

**Output**:
```markdown
## Summary
403 PERMISSION_DENIED error when publishing to Teams channel

## Environment
- **Product/Service**: Copilot Studio → Teams integration
- **Region/Version**: [REGION]

## Reproduction Steps
1. Configure agent for Teams channel
2. Attempt to publish

## Expected Behavior
Agent publishes successfully to Teams channel

## Actual Behavior
Returns `PERMISSION_DENIED` with code 403

## Error Details
```
Error: PERMISSION_DENIED
Code: 403
```

## Impact
**High** - Blocks Teams integration, regression from previous working state

## Additional Context
Was working yesterday - possible permission/config change or service regression
```
