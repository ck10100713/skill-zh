---
name: asset-audit
description: "依命名規則、檔案大小預算、格式標準稽核素材，找出孤兒素材和缺少的參照。"
argument-hint: "[category|all]"
user-invocable: true
allowed-tools: Read, Glob, Grep, Bash(stat *), Bash(file *), Bash(od *), Bash(wc *), Bash(du *)
model: sonnet
# Read-only diagnostic skill — no specialist agent delegation needed
---

# Asset Audit

## 量測檔案大小和格式需要 Bash

這個 skill 的報告要的是**檔案大小對照預算**、**貼圖尺寸**
（2 的次方）、**音訊取樣率**，還有用來偵測孤兒素材的**最後修改時間**。
這些東西 `Read`/`Glob`/`Grep` 都拿不到，要靠
`stat` 或讀二進位檔頭，所以上面已經預先核准唯讀的量測指令（`stat`、
`file`、`od`、`wc`、`du`）；列檔案用 Glob。其他任何
指令都要先問。

**量不到的數字，那個格子就填 `NOT ASSESSED`，絕對不准估。** 一張靠猜填出來的大小預算表
比空白還糟：
它看起來像證據。就算專案裡有一堆真實素材，這也是個實際存在的捏造風險：
如果範本要求填數字表格，而工具白名單
產不出這些數字，唯一能把它填完的方法就是編造。

---

## 輸入不足：產出任何報告之前先檢查這個

**如果這個 skill 需要的輸入不存在，答案是「跑不了」，
不是一份填好的報告。** 先檢查，檢查不過就停。

1. 列出這個 skill 要讀的輸入（資料檔、先前的報告、profiler 輸出、
   測試結果、registry、原始碼）。
2. 每一項都記錄 `FOUND` 或 `ABSENT`，不是「假設存在」。
3. 如果某個章節需要的任何輸入是 ABSENT，那個章節就是
   **`NOT ASSESSED — NO DATA`**。不要估，不要從
   相鄰的產物推論，也不要留一個規定要填的格子讓下一個
   讀範本的人去填。
4. 如果**所有**需要的輸入都是 ABSENT，就停下來，把
   **`NOT ASSESSED — NO DATA`** 當作整份報告的 verdict 回報，並指出缺了什麼、
   哪個 skill 會產出它。

**`NOT ASSESSED` 的 verdict 是成功。** 沒有資料時，
它就是對「資料怎麼說？」最正確、最有用的答案。它要防的失敗模式
很明確：一份 verdict 列舉裡沒有「跑不了」狀態的報告，會產生
**假的乾淨通過**：一個沒有素材也沒有標準的專案，素材稽核卻回報 COMPLIANT；
或是一份效能分析，沒有任何 profiler 資料、也從沒設過預算，卻回報「對 16.67ms 預算有 >99% 的餘裕」。

**沒有證據，不代表沒有問題。** 因為沒有檔案可掃，所以掃不到任何東西，
這並沒有驗證任何事。要說清楚是這兩種情況的哪一種，
光看綠色結果，讀的人分不出來。

---

## Phase 1: 讀取標準

讀 art bible 的 Asset Standards 章節（`design/art/art-bible.md`），以及相關設計文件裡的任何
素材標準，大小預算和格式規則都從那裡來。命名規則用下面 Phase 3 的那些，
除非 art bible 有自己的規定。art bible 要按章節讀：用
Grep 工具（pattern `^#`、content mode）找到標題，再用 offset
和 limit 讀那段範圍。

如果兩邊都沒有說明大小預算，或是根本沒有 art bible，Size 章節就是
`NOT ASSESSED — no size budget set`，報告要點名 `/art-bible`，它的
Asset Standards 章節會設定預算、格式和命名規則。

---

## Phase 2: 掃描素材目錄

素材放在引擎的素材根目錄底下：Godot 是 `assets/`，Unity 是 `Assets/`，
Unreal 是 `Content/`。依 `.claude/docs/code-root-resolution.md` 解析引擎和它的
code root；Phase 3 的孤兒素材和缺少素材搜尋就是讀這個 code root。如果解析不出來，就停下：
`NOT ASSESSED — engine unresolved`，並點名 `/setup-engine`。

用 Glob 掃描素材根目錄：

- **Godot**：`assets/art/**/*`、`assets/audio/**/*`、`assets/vfx/**/*`、
  `assets/shaders/**/*`、`assets/data/**/*`
- **Unity**：`Assets/**/*`，排除腳本（`*.cs`、`*.asmdef`）和 `*.meta` 檔
- **Unreal**：`Content/**/*.uasset` 和 `Content/**/*.umap`

比對到的檔案就是 `Total assets scanned`。如果一個都沒有，針對掃描檔案的檢查，
也就是 Naming、Size、Format、Orphaned，都是
`NOT ASSESSED — no assets under <asset root>`；缺少素材的搜尋仍然要跑。

---

## Phase 3: 執行合規檢查

**命名規則：**
- Art: `[category]_[name]_[variant]_[size].[ext]`
- Audio: `[category]_[context]_[name]_[variant].[ext]`
- 所有檔案都必須小寫，用底線連接

這些是 Godot 的慣例。Unity 和 Unreal 的素材用 PascalCase 命名，所以在
這兩個引擎上，名稱只能對照 art bible 有寫明的命名規則來檢查；
沒有規則的話，Naming 就是 `NOT ASSESSED — no naming rule for <engine>`（點名 `/art-bible`）。

**檔案標準：**
- Textures: 尺寸為 2 的次方、格式正確（UI 用 PNG，3D 用壓縮格式）、在大小預算內
- Audio: 取樣率正確、格式正確（SFX 用 OGG，音樂用 OGG/MP3）、在長度限制內。
  `file` 會回報音訊檔的格式和取樣率，但不會回報長度，而這裡
  預先核准的工具也沒有一個能量長度；所以長度預算就是
  `NOT ASSESSED — duration not measurable here`，並點名涵蓋的檔案。
- Data: 有效的 JSON/YAML，符合 schema

在 Unreal 上，素材檔（`.uasset`、`.umap`）不會保留來源檔案的
格式或尺寸，所以那裡的 Format 是 `NOT ASSESSED`；大小仍然量得到。

**孤兒素材：** 在 code root 裡搜尋每個素材檔的參照。沒有任何參照的就標記出來。

**缺少的素材：** 在 code root 裡搜尋素材參照，並確認檔案存在。

兩種搜尋都需要程式碼：如果 code root 裡沒有原始碼檔，Orphaned 和
Missing 就是 `NOT ASSESSED — no code to search`。在 Unity 和 Unreal 上，大部分素材
參照都放在 scene、prefab 和其他素材裡，不在程式碼裡，所以
沒有任何程式碼提到的素材仍可能在使用中：那裡的 Orphaned 就是 `NOT ASSESSED`。

---

## Phase 4: 輸出稽核報告

```markdown
# Asset Audit Report -- [Category] -- [Date]

## Summary
- **Total assets scanned**: [N]
- **Naming violations**: [N]
- **Size violations**: [N]
- **Format violations**: [N]
- **Orphaned assets**: [N]
- **Missing assets**: [N]
- **Sections not assessed**: [none | each section and why]

## Naming Violations
| File | Expected Pattern | Issue |
|------|-----------------|-------|

## Size Violations
| File | Budget | Actual | Overage |
|------|--------|--------|---------|

## Format Violations
| File | Expected Format | Actual Format |
|------|----------------|---------------|

## Orphaned Assets (no code references found)
| File | Last Modified | Size | Recommendation |
|------|-------------|------|---------------|

## Missing Assets (referenced but not found)
| Reference Location | Expected Path |
|-------------------|---------------|

## Recommendations
[Prioritized list of fixes, one per violation, each naming the change — the
target resolution or compression for a size violation, the corrected name for a
naming violation, the target format for a format violation]

## Verdict: [NOT ASSESSED / COMPLIANT / WARNINGS / NON-COMPLIANT]
```

依發現結果選 verdict，先符合的先贏：
- **NON-COMPLIANT**：任何大小違規，或任何程式碼有參照、但實際不存在的素材
- **WARNINGS**：只有命名、格式或孤兒素材的發現
- **NOT ASSESSED**：稽核沒有涵蓋它的範圍：完全沒有資料（上面
  那條路徑）、掃到零個素材，或是任何章節是 `NOT ASSESSED`，要點名是哪個。
  它的順位低於那兩個有發現的 verdict，因為量到的違規比
  缺口更能立刻採取行動，同時又高於 COMPLIANT
- **COMPLIANT**：至少掃過一個素材、每個章節都評估過、沒有任何發現

這個 skill 是唯讀的，只會產出報告，不會寫檔案。

---

## Phase 5: 下一步

- 用 Phase 3 的規則修正命名違規（art bible 有自己規定的話，就用它的）。
- 如果缺少標準，跑 `/art-bible` 寫它的 Asset Standards 章節。
- 人工檢查後，刪除確認過的孤兒素材。
- 跑 `/content-audit`，把素材數量和 GDD 指定的需求交叉比對。
