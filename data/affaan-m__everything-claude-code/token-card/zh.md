---
name: token-card
description: 從本機 Claude Code、Codex、Gemini CLI 和 OpenCode 的 session log，渲染出 token 用量統計卡片，並把它當成檔案 commit 進 repo。當有人想在 README 裡放目前的用量數字，或要求一張可分享的 coding-agent 活動卡片時使用。
metadata:
  origin: community
---

# Token Card

產出一張 SVG 卡片，總結這台機器上 AI coding agent 的用量：總 token 數、
等價的 API 費用、目前的連續天數，以及各 agent 之間的占比，並把它當成
README 可以引用的檔案寫進工作目錄。

這張卡片是 commit 進去的產出物，而不是託管的圖片，所以它直接從
repo 本身渲染，不依賴第三方 endpoint 一直維持運作。

## 何時啟用

- 有人想在 README 或文件頁面裡放一個看得到的用量數字。
- 有人要求跨工具的 agent 活動可分享摘要。

如果問題是「我這週花了多少」，改用 `/cost-report`。這兩個讀的
來源不同，產出的東西也不同：

| | `/cost-report` | Token Card |
|---|---|---|
| 來源 | `~/.claude/metrics/costs.jsonl`，由 ECC 的 `stop:cost-tracker` hook 寫入 | 各 agent 自己的 session log |
| Agent | Claude Code | Claude Code、Codex、Gemini CLI、OpenCode |
| 輸出 | 終端機摘要，可選 CSV | commit 進 repo 的 SVG 檔 |

## 它執行的工具

`@tokenchit/cli`，MIT 授權：<https://github.com/iyashjayesh/tokenchit>

**刻意釘在確切的版本。** `@latest` 會解析成 registry
當下提供的任何版本，而這個工具會讀本機的 session log，所以
未來一個被入侵的 release，在還沒有人審查之前，就會帶著存取那些 log 的權限被執行。要釘住版本，
並且在知情的情況下才提高它：

```bash
TOKENCHIT_VERSION=0.10.0
```

第一次執行之前，要檢查被釘住的產物：

```bash
npm view @tokenchit/cli@0.10.0 dist.integrity dist.tarball
```

## 工作流

1. **第一次下載之前先問。** `npx` 會從 npm registry 抓取套件並
   執行。那是下載遠端程式碼，而且這些程式碼會讀本機的 log，所以在這台機器上第一次執行之前，要先取得使用者的明確
   確認。如果他們拒絕，就在這裡停下來，
   並說明原本會執行什麼。

2. **設定，除非這是 dry run。** 如果沒有 `.tokenchit.json`，就執行：

   ```bash
   npx -y @tokenchit/cli@0.10.0 init
   ```

   它會偵測這台機器上哪些 agent 有 log，並記錄下來。這個檔案是設計來
   commit 的，而且絕不含任何憑證。

   **如果使用者傳了 `--dry-run`，就完全跳過這一步**，並回報 `.tokenchit.json`
   *會*被建立。會寫設定檔的預覽，不算預覽。

3. **渲染卡片。** 不帶參數的指令會寫到已設定的輸出位置，也就是 `tokenchit.svg`，
   除非 `.tokenchit.json` 指定了別的路徑：

   ```bash
   npx -y @tokenchit/cli@0.10.0 sync
   ```

   只附加使用者真正要求的 flag，每個都要照下面的拼法。不要
   把佔位符複製進指令：`sync` 會忽略不認得的位置引數，
   而不是拒絕它，所以帶方括號的 `[--dry-run]` 會被當成垃圾傳給 CLI，
   卡片照樣被寫出來，跟使用者要求的剛好相反。

   | Flag | 效果 |
   |---|---|
   | `--out <path>` | 寫到已設定輸出以外的地方 |
   | `--theme auto` \| `light` \| `dark` | 卡片主題；`auto` 會配合讀者的系統 |
   | `--dry-run` | 印出會寫入的內容，什麼都不動 |

   `sync` 讀本機檔案，不傳送任何東西：沒有 prompt、沒有程式碼、沒有檔案內容離開
   這台機器，也不會傳到任何伺服器。包在外面的 npx 呼叫是
   從 registry 下載，這就是這個工作流裡的網路存取，而步驟 1 就是
   取得同意的地方。

4. **回報並提議。** 印出它產生的數字（token、等價費用、連續天數、
   各 agent 占比）和寫入的路徑。如果 repo 有 README 還沒有
   引用這張卡片，就提議加上：

   ```markdown
   ![tokenchit](./tokenchit.svg)
   ```

   `sync` 印出的是相對於 repo 根目錄的路徑。Markdown 圖片是相對於
   它所在的檔案解析的，所以要依正在編輯的 README 重寫：位於
   `docs/usage.svg` 的卡片，從根目錄的 README 是 `./docs/usage.svg`，但從
   `docs/zh-CN/README.md` 是 `../usage.svg`。把印出來的路徑直接貼進巢狀的 README，
   會指到 `docs/zh-CN/docs/usage.svg`，渲染會壞掉。

   沒被要求就不要編輯 README。

做完步驟 4 就停。發布到公開排行榜是另一個 `publish` 指令，
需要明確選擇加入，不屬於這個工作流，只有使用者指名要求時才執行。
`unpublish` 會再次移除那一列和帳號。

## 輸出

SVG 的路徑、它包含的數字，以及引用它的 markdown 片段。
dry run 時：會寫入什麼，而磁碟上什麼都沒有改變。

## 備註

- 需要 Node.js 22 或更新的版本（套件宣告了 `engines: { node: ">=22" }`）。沒有東西
  是全域安裝的；`npx` 每次執行都會抓取被釘住的版本。
- 只讀 token 數和時間戳。
