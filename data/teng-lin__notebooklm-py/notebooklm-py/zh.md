---
name: notebooklm
description: 透過 notebooklm-py CLI 或有型別的 async Python API 來安裝、驗證、排錯並操作 Gemini Notebook。當使用者提到 Gemini Notebook、notebooklm-py、notebooklm CLI 或它的 Python API，需要管理 notebook 與來源、做有依據的對話與研究、產生或下載 artifact 時使用。一般的 Gemini API 或無關的內容創作不要用這個。
---

# Gemini Notebook 自動化

agent 工作流一律用 `notebooklm` CLI。優先加 `--json` 並明確指定 ID，這樣每個操作都看得到、並行時也安全。只有在使用者要求應用程式碼、或 CLI 做不到那個流程時，才用有型別的 async Python API。下面關於就緒狀態、身分、授權和憑證處理的規則，兩種介面都適用。

## 安裝與驗證

需要 Python 3.10+。裝在使用者現有的環境裡，除非對方要求，否則不要另外建環境：

```bash
pip install "notebooklm-py[browser]"
pip install "notebooklm-py[cookies]"  # optional browser-cookie extraction
```

如果系統的 `pip` 回報 `externally-managed-environment`，不要用 `--break-system-packages`。只用 CLI 的話，建議用 `uv tool install "notebooklm-py[browser]"` 或等效的 `pipx` 指令；要寫應用程式碼，就用使用者目前啟用的專案環境。

無人值守或 headless 的情況，優先用持久的、綁 profile 的 master-token 驗證，不要用複製來的 cookie 快照。安裝 `pip install "notebooklm-py[headless]"`；第一次自動擷取 OAuth 還需要 `[browser]`。在可信任的工作站上執行 `notebooklm login --master-token --account <email>`，然後把 `master_token.json`（不是 `storage_state.json`）部署到選定的 profile。`NOTEBOOKLM_HOME` 指定私有的基底目錄，`NOTEBOOKLM_PROFILE` 指定 profile；預設會解析成 `~/.notebooklm/profiles/default/master_token.json`。

在 CI 裡，`NOTEBOOKLM_MASTER_TOKEN_JSON` 只是傳遞 secret 的慣例，不是套件會直接讀的環境變數。把它的原始值用 `0600` 權限寫進選定 profile 的 `master_token.json`，然後 unset 它，再執行 `notebooklm auth refresh` 產生 `storage_state.json`。同一個 profile 裡的 master token 可以自動重新產生過期的檔案型 cookie。行內的 `NOTEBOOKLM_AUTH_JSON` 只是短期的備案；它會繞過這條恢復路徑。

用 PyPI 或 release tag，不要用未發布的 `main` checkout。有的話可以參考[安裝指南](https://github.com/teng-lin/notebooklm-py/blob/main/docs/installation.md)。

跑工作流之前，要確認真的驗證成功，不要只是解析 cookie 檔：

```bash
notebooklm auth check --test --json
```

要求 `.status == "ok"` 而且 `.checks.token_fetch == true`。如果驗證失敗：

- 有螢幕的話，執行 `notebooklm login` 再驗證一次。
- headless 環境下，安裝 `[cookies]` 並用 `notebooklm login --browser-cookies <browser>`。帳號不確定要選哪個時，先用 `notebooklm auth inspect --browser <browser>`。
- 如果原本有效的 cookie 變舊了，先試 `notebooklm auth refresh`；在瀏覽器重新登入後，用 `notebooklm auth refresh --browser-cookies <browser>`。

一般的 `--test` 預檢可能會自動修復並保存更新後的 cookie。如果檢查必須嚴格唯讀（包括下面的失敗診斷流程），加上 `--passive`。

`notebooklm status` 回報的是目前選中的 notebook 情境，不是驗證狀態。

兩個驗證檔都當成 bearer 憑證處理：絕對不要印出、記錄或 commit。master token 是持久的完整帳號憑證，改密碼也不會失效；要用專用帳號、存在 secret store、磁碟上設成 `0600`，外洩的話要明確撤銷。

## 操作不變式

1. 探索和變更操作都用 `--json`，然後保留回傳的完整 UUID。重要的回傳欄位有：`create` 的 `.notebook.id`、`source add` 的 `.source.id`、非同步 generator 的 `.task_id`。`generate mind-map` 則是回傳 `mind_map`、`note_id` 和 `kind`；兩種 kind 都直接回傳完成的結果，沒有 task ID，也不需要另外跑 `artifact wait`。
2. 自動化或並行工作時，每個屬於某個 notebook 的指令都要帶 `-n/--notebook <id>`。不要依賴 `notebooklm use`。每個並行的執行還要設一個獨一無二的 `NOTEBOOKLM_PROFILE=agent-<id>`，讓 context 和 profile 的寫入互相隔離。新 profile 沒有憑證：要把 `master_token.json` 的副本放進那個 profile，並在使用前先產生它的 storage。絕對不要讓多個 agent 共用同一個可寫的 `storage_state.json`。
3. 加完來源之後，保留每個 `.source.id`，然後在 chat 或 generation 之前，對每個都跑 `source wait`。add 的回傳沒有 status。要求 wait 的 exit code 是 0 而且 `status == "ready"`；針對特定媒體的暫時性 `error` 列，讓 waiter 自己處理。
4. 非同步 generator 回傳 task/artifact ID 之後，把它當位置參數傳給 `artifact wait`，並帶 `-n <notebook_id>`。要下載就用 `-a <artifact_id> -n <notebook_id>` 精確指定那個 artifact；絕對不要選「最新看得到的 artifact」。Mind-map 的產生會直接回傳完成的結果，不需要 `artifact wait`。
5. 有重疊的 research 執行，一律帶 `--run-id <research_run_id>`。
6. 只有 host 真的有背景執行功能時才用。wait 和依賴它的 download 指令要放在同一個循序的 job 裡，而且 wait 以 exit 0 結束後才能下載。否則就在前景執行，或把明確指定 ID 的指令交還給使用者。

## 授權邊界

安全的檢視，以及使用者明確要求的建立、加入來源、chat、提示詞建議，可以直接執行。要恢復之前，先用唯讀指令診斷失敗原因。

如果某個動作事先沒有被明確授權，就在執行前立刻取得確認：

- 破壞性指令，例如刪除 notebook/來源/note/artifact/label/profile、移除分享、logout、clear、取消 research，以及 `ask --new`；
- `language set`，因為預設模式會改掉整個帳號的輸出語言（建議改用 generation 指令的 `--language` 覆寫）；
- 產生內容或長時間的前景等待，這些可能要好幾分鐘，也可能被限流；
- 下載，因為會寫檔；
- `research wait --import-all`，因為會匯入來源；
- `ask --save-as-note` 和 `history --save`，因為會建立 note。

授權的邊界是使用者的意圖，不是 CLI 有沒有跳出提示。取得授權後，在支援的指令上帶 `--yes`/`-y`。大多數有破壞性的 JSON 指令沒帶它就會拒絕提示，但有些（包括 `ask --new --json` 和 `share remove --json`）會不經提示直接執行。絕對不要把「沒有提示」當成同意。

`research cancel` 是送出就不管的。取消經過授權後，用 `notebooklm research status -n <notebook_id> --run-id <research_run_id> --json` 確認那個 run 的狀態。

## 指令探索

以安裝的 CLI 的 help 為準（跟版本相符），不要憑空猜 flag：

```bash
notebooklm --help
notebooklm source --help
notebooklm research --help
notebooklm generate --help
notebooklm artifact --help
notebooklm download --help
```

另外也要看 `notebooklm --version`，當某個指令的 help 跟這個 skill 不一樣時，往下查到那個確切的指令，例如 `notebooklm generate audio --help`。

常見操作：

| 目標 | 指令 |
|---|---|
| 查看運算用量 | `notebooklm usage --json`；`notebooklm usage --categories` 可看各類別的可用性和預估費用 |
| 列出或建立 notebook | `notebooklm list --json`；`notebooklm create "Title" --json` |
| 加入來源並等待 | `notebooklm source add <input> -n <nb> --json`；`notebooklm source wait <src> -n <nb>` |
| URL 恢復 | `notebooklm source add <url> --fallback-fetch` |
| 對話 | `notebooklm ask "question" -n <nb> --json` |
| 研究 | `notebooklm source add-research "query" -n <nb> --mode fast --json`（也支援 `deep`） |
| 列出或等待 artifact | `notebooklm artifact list -n <nb> --json`；`notebooklm artifact wait <id> -n <nb>` |
| 產生 | `notebooklm generate <type> ... -n <nb> --json` |
| 下載 | `notebooklm download <type> <path> -n <nb> -a <artifact>` |

完整的指令範圍請查已安裝的指令 help，有的話也可以看 [CLI 參考文件](https://github.com/teng-lin/notebooklm-py/blob/main/docs/cli-reference.md)。寫應用程式碼的話，用下面的基準範例，有的話也可以看 [Python API 指南](https://github.com/teng-lin/notebooklm-py/blob/main/docs/python-api.md)。

## 標準的「來源到 Artifact」流程

從 JSON 輸出裡保留 `{notebook_id}`、每個 `{source_id}` 和 `{artifact_id}`：

如果使用者明確要求跑完這整套流程，就等於授權了其中正常的前置等待、要求的產生動作和要求的輸出檔。只有這個要求沒涵蓋的工作才需要確認。

1. `notebooklm create "Research: topic" --json`
2. 每個輸入都跑 `notebooklm source add <input> -n {notebook_id} --json`。
3. 前景等待獲得授權後，對每個擷取到的來源跑 `notebooklm source wait {source_id} -n {notebook_id} --timeout 600`。
4. 產生動作獲得授權後，產生要求的類型。以 audio 為例：`notebooklm generate audio "instructions" -n {notebook_id} -s {source_id} --json`。每個選定的來源都重複一次 `-s`，並把 `.task_id` 擷取成 `{artifact_id}`。
5. 前景等待獲得授權後，執行 `notebooklm artifact wait {artifact_id} -n {notebook_id} --timeout 1200`。
6. 輸出寫檔獲得授權後，執行 `notebooklm download audio ./podcast.m4a -a {artifact_id} -n {notebook_id}`。

如果只要分析、不要產生內容，就把第 4 到 6 步換成明確指定 ID 的 chat 指令，而且要等每個來源都 ready 才能下：

```bash
notebooklm ask "Summarize the key arguments" -n {notebook_id} --json
```

## 深度研究

深度研究可能要 15 到 30 分鐘以上。用不阻塞的方式啟動，並把 `.poll_task_id // .task_id` 留下來當 `{research_run_id}`：

```bash
notebooklm source add-research "query" -n {notebook_id} --mode deep --no-wait --json
```

要明確授權後才能匯入，而且兩個 ID 都要指定：

```bash
notebooklm research wait -n {notebook_id} --run-id {research_run_id} \
  --import-all --timeout 1800 --json
```

用 `--import-all` 時，`--timeout` 是輪詢和匯入重試各階段各自的預算，所以這個範例大概會花掉約 3600 秒的 host 實際時間。

把新建立的來源 ID 從 `.imported_sources[].id` 留下來，後續 chat 或 generation 之前先等它們 ready。

## Python API 基準範例

拿不到完整 API 指南時，用已安裝的有型別 API 和它的 docstring，不要猜方法名稱。要沿用跟 CLI 流程一樣的 ID 和就緒檢查：

```python
import asyncio

from notebooklm import NotebookLMClient


async def main(url: str) -> None:
    async with NotebookLMClient.from_storage() as client:
        notebook = await client.notebooks.create("Research: topic")
        source = await client.sources.add_url(notebook.id, url)
        await client.sources.wait_until_ready(notebook.id, source.id, timeout=600)

        answer = await client.chat.ask(
            notebook.id, "Summarize the key arguments", source_ids=[source.id]
        )
        print(answer.answer)

        task = await client.artifacts.generate_audio(
            notebook.id,
            source_ids=[source.id],
            instructions="Focus on the key arguments",
        )
        final = await client.artifacts.wait_for_completion(notebook.id, task.task_id, timeout=1200)
        if not final.is_complete:
            raise RuntimeError(f"Generation ended with {final.status}: {final.error}")
        await client.artifacts.download_audio(
            notebook.id, "./podcast.m4a", artifact_id=task.task_id
        )


asyncio.run(main("https://example.com"))
```

`NotebookLMClient.from_storage()` 是 async context manager，不用 await。client 在同一個 event loop 上可以重入，但不是 thread-safe；每個 loop 建一個 client。公開的 namespace 有 `notebooks`、`sources`、`chat`、`research`、`artifacts`、`mind_maps`、`notes`、`settings`、`sharing`、`labels` 和 `collections`。執行會改變狀態、耗時很長或會寫檔的呼叫之前，要先套用上面的授權邊界。

## 產生內容的注意事項

可用的 generator 有 `audio`、`video`、`slide-deck`、`infographic`、`report`、`mind-map`、`data-table`、`quiz` 和 `flashcards`。要看 `notebooklm generate <type> --help`，因為格式、風格、來源選擇、語言和重試支援會依類型不同。

這幾個不明顯的差異要記得：

- Mind map（`--kind interactive`，預設）內部是非同步的 studio artifact，但 CLI 會輪詢到完成並回傳 `{mind_map, note_id, kind}`；不要再跑 `artifact wait`。
- Mind map（`--kind note-backed`）是伺服器同步的。兩種都接受 `--instructions`；interactive 會確實套用，note-backed 的伺服器端可能會忽略。
- `generate video --format cinematic` 會忽略 `--style`，需要 Google AI Ultra，而且可能要大約 30 到 40 分鐘。
- Slide-deck 沒有方向的 flag。要直式輸出就在描述裡講（例如 `9:16 portrait`）；修改投影片時不能改變整份的方向。
- 自訂報告要用 `--format custom`，並把 prompt 當位置參數的描述傳進去；`--append` 只適用於內建的報告格式。

如果 prompt 太長、或用 shell 引號很麻煩，可以在 `ask`、`source add-research` 和支援的 generator 上用 `--prompt-file PATH`。它裝的是 prompt 文字；要上傳來源文件就用 `source add`。

## 輸出與引用

結構化地用 JSON，不要去解析給人看的輸出。常見的生命週期值：

- 來源：`unknown`/`preparing`/`processing` -> `ready` 或 `error`；只有 `ready` 才能繼續；
- artifact：`pending`/`in_progress` -> `completed`、`failed` 或 `removed`；`not_found` 可能只是列表短暫延遲。只有 `completed` 才能繼續或下載。

Chat 的 JSON 包含 `answer`、`conversation_id` 和 `references[].source_id`。引用的 `start_char`/`end_char` 是結構化來源文件裡的 UTF-16 offset，不是平面的 `SourceFulltext.content`。在 Python 裡，用 `from notebooklm import resolve_chat_reference_passage`，然後呼叫 `await resolve_chat_reference_passage(client, notebook_id, reference)`；它會用精確的文件範圍，必要時退回 `find_citation_context()`。

## 失敗處理

失敗時，先跑安全的唯讀診斷：

```bash
notebooklm auth check --test --passive --json
notebooklm list --json
notebooklm source list -n {notebook_id} --json
notebooklm artifact list -n {notebook_id} --json
notebooklm research status -n {notebook_id} --run-id {research_run_id} --json
```

只檢查跟失敗流程相關的指令。診斷期間不要改變任何狀態。

- Exit 0 代表成功。預期內的指令失敗用 exit 1。`source wait` 逾時用 exit 2；`artifact wait` 和 `research wait` 逾時用 exit 1。
- 先看 exit code 再分支。一般已處理的 JSON 失敗用 `{error, code, message}`，而 wait 指令會回傳領域專屬的結構，例如 `{"status": "timeout", "error": "..."}`。
- 驗證失敗時，重新檢查 `checks.token_fetch`；不是 `true` 才去登入。
- wait 逾時的話，回報它，並檢查那個確切的來源、artifact 或 research run。
- Google 會對 generation 限流。保留 task ID、檢查狀態，只有使用者授權才重試；不要無限迴圈。對於已經失敗的 Studio artifact，原地重試之前先看 `notebooklm artifact retry <artifact_id> -n {notebook_id} --help`。
- 遇到協定錯誤時，記下安裝的版本、確切的指令、相關的 ID 和已遮蔽的錯誤訊息。有網路的話去查專案的 issue tracker；沒有網路就不要自己編 workaround。

進度更新要簡短，並附上相關的回傳 ID。絕對不要洩漏憑證內容。

## 安裝 Skill

如果這個檔案已經在 agent 的 skill 目錄裡，代表 skill 已經裝好了。否則：

- `notebooklm skill install` 會安裝或更新支援的本機 skill 目標。
- `notebooklm skill package` 會建出可上傳的封存檔，給沙盒化的 agent 環境用。
- `notebooklm skill status --json` 會回報已安裝的版本和 `content_mismatch`。
