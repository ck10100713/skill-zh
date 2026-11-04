---
name: brand-discovery
description: 跨 8 個模組（目的、定位、受眾、個性、語調、敘事、創辦人張力）進行結構化、可中斷續跑的多場次品牌識別訪談，運用階梯式追問、5 Whys 和投射技巧，把答案存到磁碟，最後產出主品牌手冊（90_SYNTHESIS.md）。適用於建立或重新定位品牌、向設計師或寫手交辦需求，或把創辦人腦中的隱性知識講清楚。
---

# Brand Discovery

用這個 skill 進行一場結構化、會隨答案調整的品牌識別訪談。
最終目標是一份完整的 `90_SYNTHESIS.md`，也就是一本主品牌手冊，
組織可以拿它去向設計師、寫手和外部合作夥伴交辦工作。

訪談會跨好幾個場次進行。邊問邊把答案存到磁碟，
這樣對話結束時問出來的東西不會流失，
之後的場次也能從上次停下來的地方接著做。

## When to Activate

- 正在建立品牌、重新定位品牌，或需要一份書面的品牌識別參考文件來向合作夥伴交辦。
- 預期會有多個場次，對話會橫跨好幾天或好幾週。
- 有多位創辦人或利害關係人，需要先各自訪談，再做整合。
- 使用者想要的是結構化、可重複的方法，而不是隨興聊天。
- 現有的品牌文件零散、隱性，或要靠創辦人本人才講得清楚，需要把它們明確寫下來。

## Session start protocol

每次啟動時，在問任何訪談問題**之前**，先做這幾步：

1. **檢查先前的進度。** 在專案的 brand-identity 目錄裡找現有的模組檔案
   和 `state.json` checkpoint。
   如果都沒有，就是全新開始：先確認品牌名稱、
   參與者，以及 brand-identity 檔案要存在哪裡，然後從第一個模組開始。
2. **讀目前進行中的模組檔**（如果有的話），掃過它的 Raw
   區塊，看之前記下哪些答案。
3. **向使用者回報**，用兩三句話講：目前在哪個模組、
   狀態如何、還剩什麼。然後問：「要從這裡繼續，還是換模組？」

## Interview discipline

每個模組都要遵守這些規則：

1. **一次只問一個問題。** 絕對不要丟出一整串問題。
2. **每次回答之後：** 簡短複述 → 再做一個深入追問，或者
   如果這個主題已經飽和就收掉這條線。不准默默跳到下一題。
3. **階梯式追問（Laddering）：** 對每個「是什麼」的回答，接著問
   「這對你為什麼重要？」，一直問到核心價值浮現（通常兩到四輪）。
4. **5 Whys：** 針對信念或定位主張，一路追到根本原因，
   不要停在表面的宣告。
5. **察覺薄弱的回答：** 如果答案很籠統、滿是行話或很模糊，就請對方舉
   一個具體例子、一個客戶故事，或一個數字。
6. **投射技巧**（每個模組用一次，用來突破停滯期）：
   - 「如果這個品牌是一個人，他會怎麼走進一個房間？」
   - 品牌訃聞：「如果這個組織五年後關門了，客戶會懷念什麼？
     你會後悔沒說出口的又是什麼？」
   - 競爭對照：「說一個你欣賞、但絕對不想變成的同業。
     他具體哪裡是錯誤的範本？」
7. **飽和訊號：** 連續兩次追問都沒有帶出新資訊時，就做摘要
   並結束這個模組。
8. **模組結尾：** 寫一份結構化的模組檔，分成兩個區塊：
   - `## Raw`：逐字引述和例子。
   - `## Synthesis`：你的詮釋、三個候選表述、
     未解的問題、參與者之間的矛盾。
   然後更新 `state.json` checkpoint（見下面的 State protocol）。

## Module sequence

| File | Label | Frameworks used |
|------|-------|-----------------|
| `10_purpose-why.md` | Purpose / Why | Sinek Golden Circle, Lencioni |
| `20_positioning.md` | Positioning | Dunford "Obviously Awesome", Moore template |
| `30_audience-niche.md` | Audience & Niche | Baker "Business of Expertise", ICP |
| `40_personality-archetype.md` | Personality & Archetype | Mark & Pearson 12 archetypes, J. Aaker 5 dims |
| `50_voice-tone.md` | Voice & Tone | Brand voice guidelines |
| `60_narrative-story.md` | Narrative / Story | Neumeier trueline, brand story arc |
| `70_founder-tension.md` | Founder Brands vs Studio Brand | Enns "Win Without Pitching" |
| `90_SYNTHESIS.md` | Master Brandbook | Kapferer prism, Aaker brand system |

模組照順序做。使用者要求跳模組就照辦，
並在 `state.json` 裡記下跳過了哪個。

## State write protocol

每個模組達到飽和或完成狀態後，寫兩個檔案：

**模組檔**放在 `modules/{moduleFile}`，內容是完整的 Raw 和 Synthesis。

**`state.json`** 是輕量的 checkpoint，讓之後的場次可以接著做。
更新 `completedModules`、`inProgressModule`、`nextModule`、`lastUpdated`。
Schema：

```json
{
  "session": "{brand_name}-brand-{YYYY-MM}",
  "outputPath": "{path_to_brand_identity_directory}",
  "completedModules": [],
  "inProgressModule": "10_purpose-why.md",
  "nextModule": "20_positioning.md",
  "participants": ["founder-A"],
  "lastUpdated": "{ISO-8601}"
}
```

寫完之後確認：「Module X saved. State updated. Next: Y.」

**最後一個模組（90_SYNTHESIS.md）：** 寫最終整合時，
在 `state.json` 把 `inProgressModule` 設成 `"90_SYNTHESIS.md"`，
`nextModule` 設成 `null`。寫完後，把 `"90_SYNTHESIS.md"` 加進 `completedModules`，
再把 `inProgressModule` 設成 `null`。如果留著不清掉，
之後續跑時會把已完成的品牌手冊當成還在進行中。
然後確認：「Brandbook complete. All modules saved.」

## Multi-founder mode

不只一位創辦人參與時，把每位創辦人的答案寫到
`founders/{participant}.md`，不要寫進主模組檔。寫入前先驗證
`participant` 名稱：只接受英數字和連字號
（例如 `founder-a`、`anna`）；拒絕含路徑分隔符號
（`/`、`\`、`..`）或特殊字元的名稱。`moduleFile` 要對照
列舉出來的模組順序驗證（只能是 10 到 90）。`outputPath` 要驗證
它是專案目錄內的絕對路徑，相對路徑和用 `..` 跳出去的路徑一律拒絕。
所有創辦人都完成某個模組後，跑一次整合：在模組檔裡摘要
共識與分歧，並標出「有建設性的張力」，留給團體對齊工作坊討論。

## Anti-Patterns

- **沒先讀 state 就開始。** 每個場次一開始都必須先檢查現有的模組檔和 `state.json`。跳過這步，前面場次累積的脈絡就全丟了。
- **一次問好幾個問題。** 一次一個問題沒有商量餘地，列清單只會得到打勾式的答案，問不出真正的洞見。
- **還沒飽和就進 Synthesis。** 如果最後兩次追問都沒帶出新資訊，這個模組就做完了；如果有，就還沒完。
- **跳過多創辦人整合。** 有多位利害關係人時，必須先完成各自的訪談再整合。一開始就集體討論品牌，會引入錨定偏誤。
- **把這當成一次就結束的場次。** 這個 skill 設計給多場次使用。在一場對話裡硬衝到 `90_SYNTHESIS.md`，產出會很淺。

## Related Skills

- `competitive-platform-analysis`：brand-discovery 把定位簡報確立之後，用這個 skill 來界定並分類競爭對手集合。
- `brand-voice`（ECC）：如果 brand-discovery 的語調模組需要另外一份從來源推導出來的寫作風格檔案。
