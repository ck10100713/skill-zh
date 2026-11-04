---
name: wizard
description: 產生一支互動式 bash wizard，帶人類走過只有他們自己能做的步驟。用於佈建基礎設施、設定憑證或 CI secret、走過不熟悉的第三方 dashboard，或執行一次性的遷移或切換。agent 自己能做的步驟不要用這個。
---

# Wizard

**wizard** 是一支 bash 腳本，一步一步帶人類走過一套手動流程，這種流程親手做很煩，每次都要重新向 AI 解釋也很煩。它會打開每個 URL、明確說出要點哪裡和複製什麼、擷取這些值、把它們寫到該去的地方（`.env`、GitHub secrets）、在每個階段都確認，並顯示還剩幾個階段。它可以設定第三方服務、執行一次性的遷移，或把專案從一種狀態搬到另一種。

讓人愉快的 UX 已經由 [template.sh](template.sh) 解決了：逐階段的進度、確認關卡、跨平台開 URL（包括 WSL）、隱藏的 secret 輸入、冪等的 `.env` upsert、`gh secret`/`gh variable` 寫入，以及結尾的摘要。**你的工作只是界定流程範圍，並撰寫它的各個階段。** `STAGES` 標記以上的函式庫在每個 wizard 裡都完全相同；這種一致性就是重點：絕對不要手動編輯它。

wizard 預設是短命的：為了一次執行而建，存到暫存或 `scripts/` 路徑，工作做完就刪掉。只有在使用者想要一條可重複的設定路徑、而且該放在 repo 裡時，才 commit 它。

## 流程

### 1. 界定流程範圍

釐清人類必須做的每個手動步驟，以及沿途要擷取的每個值。先讀 repo，不要冷冰冰地開口問：

- 設定類：`.env`、`.env.example`、`.env.*`、`README`、`docker-compose*`、framework 設定，以及 `.github/workflows/*`（每個 `secrets.*` / `vars.*` 的參照，都是 wizard 必須產出的值）。
- 遷移或轉換類：目前的狀態、目標的狀態，以及兩者之間不可逆的動作。

然後給使用者看依序排列的階段清單和每個階段產出的值，並確認：他們可以增加、刪除或重新排序。

**完成的標準：** 每個階段都依序命名，而且對每個擷取的值，你都知道 (a) 人類從哪裡拿到它、(b) 它寫到哪裡（`.env`、GitHub secret、兩者都寫，或哪裡都不寫；有些階段只是純動作）、(c) 它是 secret（隱藏輸入）還是公開的。

### 2. 描繪每個階段的路徑

對每個階段，寫出人類要走的精確路徑：要開哪個 URL、在那裡做什麼、值顯示在哪裡、它要填入哪個變數：例如「Dashboard → Developers → API keys → Reveal test key → copy」。如果你其實不知道目前的 UI 或確切的指令，就直說，並問使用者或查文件：絕對不要編造可能不存在的步驟。

**完成的標準：** 每個階段都能對應到陌生人也能照著做的具體指示。

### 3. 撰寫 wizard

把 `template.sh` 複製到目標路徑。把範例階段換成每個步驟各一個 `stage`，依依賴順序排列。使用函式庫的輔助函式：`stage`、`say`/`step`、`open_url`、`ask`/`ask_secret`、`write_env`、`set_secret`/`set_var`、`pause`/`confirm`。把 `TOTAL_STAGES` 設成你寫的階段數。

守住 template 設下的標準：先打開 URL 再問它的值、任何 secret 都用 `ask_secret`、每個要持久保存的值都 `write_env`、只有 CI 真的需要的值才 `set_secret`，以及在任何不可逆的動作之前先 `confirm`。每個 `stage` 都會清除畫面，只留下目前的步驟：一個階段只放一個專注的任務，這樣人類需要的東西才不會捲走。不要碰標記以上的函式庫。

### 4. 驗證並交接

- `bash -n <script>`；如果有 `shellcheck` 就跑它。
- `chmod +x <script>`。
- 不要自己從頭到尾執行它：它會開瀏覽器，並卡在等人類輸入。改用靜態方式追蹤：第 1 步的每個值都有被擷取，並且落在第 1 步說的地方，而且每個 `set_secret` 的名稱都跟 CI 裡的某個 `secrets.*` 參照完全吻合。
- 告訴使用者怎麼執行它。如果它是可重複的設定路徑，就 commit 它並從 README 連結過去，這樣下一個人就是執行腳本，而不是去問 AI。
