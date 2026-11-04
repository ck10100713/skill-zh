---
name: cost-tracking
description: 從本機 ECC cost-tracker 的 metrics log 追蹤並回報 Claude Code 的 token 用量、花費和預算。當使用者問到成本、花費、用量、tokens、預算，或想依模型、session、日期看成本明細時使用。
metadata:
  origin: community
---

# 成本追蹤

用這個 skill 來分析 Claude Code 的成本與用量紀錄，資料來源是 ECC 的 `stop:cost-tracker` hook 寫出來的 metrics log。

## 資料放在哪

tracker 每次 session 結束（stop）就在 `~/.claude/metrics/costs.jsonl` 追加一個 JSON 物件。每一列都是**該 session 的累計快照**，所以要算總花費，得**每個 `session_id` 只取最新的那一列**，再把各 session 加總，每一列都加的話會重複計算。

ECC 還會在 `~/.claude/metrics/cost-snapshots/` 底下維護內部的 per-session 檔案，讓 runtime hook 不用重掃整份歷史就能讀到目前 session 的總額。把這些檔案當成可以重建的快取就好；每份 snapshot 都存了一個 byte cursor，只會掃新追加的列。穩定狀態下讀取是 O(1)，更新是 O(新增的 bytes)。過期的項目會在 30 天後，或目錄超過 512 個 session 時清掉。冷啟動補資料的工作，每次 hook 呼叫上限 16 MiB，超過 1 MiB 且沒有換行結尾的壞掉列會被丟掉，並保留可以接續的 cursor。報表和匯出還是一律用 `costs.jsonl`。

每列的 schema：

| 欄位 | 意義 |
| --- | --- |
| `timestamp` | 快照的 ISO 時間戳 |
| `session_id` | Claude Code 的 session 識別碼 |
| `transcript_path` | session transcript 的路徑 |
| `model` | 使用的模型 |
| `input_tokens` / `output_tokens` | token 數量 |
| `cache_write_tokens` / `cache_read_tokens` | prompt cache 的 token 數量 |
| `estimated_cost_usd` | 預先算好的該 session 累計成本（美元） |

要用 `estimated_cost_usd`，不要自己手算價格，因為模型和 cache 的價格會變，tracker 才是 source of truth。

## 何時使用

- 使用者問「我花了多少？」「這個 session 花了多少？」或「我的 token 用量是多少？」
- 使用者提到預算、花費上限、超支或成本控管。
- 使用者想依模型、session 或日期看成本明細，或要匯出 CSV。

## 運作方式

先確認 log 存在（用 `node`，不要用 `sqlite3`，因為 tracker 寫的是 JSONL，而且 `node` 跨平台）：

```bash
node -e 'const fs=require("fs"),os=require("os"),p=require("path");const f=p.join(os.homedir(),".claude","metrics","costs.jsonl");console.log(fs.existsSync(f)?"cost log found":"cost log not found: "+f)'
```

如果 log 不存在，不要編造用量資料。直接告訴使用者：要在啟用 `stop:cost-tracker` hook 的狀態下跑完第一個 session，成本追蹤才會有資料。

## 範例：摘要、依模型分組、最近 7 天

```bash
node -e '
const fs=require("fs"),os=require("os"),path=require("path");
const f=path.join(os.homedir(),".claude","metrics","costs.jsonl");
if(!fs.existsSync(f)){console.log("cost log not found: "+f);process.exit(0);}
const rows=fs.readFileSync(f,"utf8").split(/\r?\n/).filter(Boolean).map(l=>{try{return JSON.parse(l)}catch{return null}}).filter(Boolean);
const bySession=new Map();
for(const r of rows){const k=r.session_id||r.transcript_path||r.timestamp;const p=bySession.get(k);if(!p||String(r.timestamp)>String(p.timestamp))bySession.set(k,r);}
const latest=[...bySession.values()];
const cost=r=>Number(r.estimated_cost_usd)||0, day=r=>String(r.timestamp||"").slice(0,10), sum=a=>a.reduce((s,r)=>s+cost(r),0), f4=n=>"$"+n.toFixed(4);
const today=new Date().toISOString().slice(0,10), yest=new Date(Date.now()-864e5).toISOString().slice(0,10);
console.log("today: "+f4(sum(latest.filter(r=>day(r)===today)))+" | yesterday: "+f4(sum(latest.filter(r=>day(r)===yest)))+" | total: "+f4(sum(latest))+" ("+latest.length+" sessions)");
const m=new Map();for(const r of latest){const k=r.model||"(unknown)";m.set(k,(m.get(k)||0)+cost(r));}
console.log("by model:");[...m.entries()].sort((a,b)=>b[1]-a[1]).forEach(([k,v])=>console.log("  "+f4(v)+"  "+k));
'
```

要看單一 session 的細節或匯出 CSV，就對同一個 `latest` 集合（CSV 的話用原始 rows）跑迴圈，印出你要的欄位。

## 回報指引

呈現成本資料時，要包含今天和昨天的花費對比、所有 session 的總額、依模型的明細，以及 session 數量。不到一美元的金額顯示四位小數，更大的金額顯示兩位。

## 反模式

- 不要把每一列都加總，它們是每個 session 的累計值；要先縮減成每個 `session_id` 的最新一列。
- 有 `estimated_cost_usd` 的時候，不要用原始 token 數去估成本。
- 不要沒檢查就假設 log 存在。
- 不要在給使用者的回答裡寫死目前的模型價格。
- 不要推薦安裝沒審查過、會執行任意程式碼的 hook 或 plugin。

## 相關

- `/cost-report` - 針對同一份 metrics log 的指令版報表。
- `cost-aware-llm-pipeline` - 模型路由與預算設計的模式。
- `token-budget-advisor` - context 與 token 預算規劃。
- `strategic-compact` - 用 context 壓縮來減少重複花費的 token。
