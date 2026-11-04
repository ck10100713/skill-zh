---
name: ux-review
description: "驗證 UX 規格、HUD 設計或 pattern library：無障礙、GDD 對齊、是否準備好進入實作。結論分 APPROVED / NOT ASSESSED / NEEDS REVISION / MAJOR REVISION NEEDED。"
argument-hint: "[file-path or 'all' or 'hud' or 'patterns']"
user-invocable: true
allowed-tools: Read, Glob, Grep, Bash(bash "*/.claude/skills/ux-review/../../hooks/yaml-helper.sh" resolve_config *)
model: sonnet
---

!`bash "${CLAUDE_SKILL_DIR}/../../hooks/yaml-helper.sh" resolve_config --keys workflow`

上面已經解析好了，直接用。如果沒有這個區塊，就用
`.claude/docs/config-resolution.md` 裡的預設值。

# UX Review

## Overview

在 UX 設計文件進入實作流程之前先驗證。
它是 `/team-ui` pipeline 裡 UX Design 和 Visual Design／實作之間的品質關卡。

**這個 skill 在這些時機跑：**
- 用 `/ux-design` 完成 UX 規格之後
- 交給 `ui-programmer` 或 `art-director` 之前
- Pre-Production 到 Production 的關卡檢查之前（關卡要求關鍵畫面都有審過的 UX 規格）
- UX 規格大改之後

**結論等級：**
- **APPROVED**：規格完整、一致，可以直接實作
- **NOT ASSESSED**：有一個或多個審查維度找不到可比對的準則，或規格讀不到，要指明是哪一項
- **NEEDS REVISION**：發現具體缺口，交接前要修，但不用整個重設計
- **MAJOR REVISION NEEDED**：範圍、玩家需求或完整性有根本問題，需要大幅重做

**`NOT ASSESSED` 的排序高於 APPROVED，低於兩個 revision 結論。** 沒辦法評估某個維度的審查，不能證明規格已經可以實作；但別人找到的缺口比沒人能檢查的缺口更有行動價值，所以它不能蓋過這兩個結論。這個結論出現的時機：規格檔讀不到、檢查清單的某個維度沒有可比對的 source of truth、或無障礙等級沒有定案（見下方）。

---

## Phase 1: Parse Arguments

- **指定檔案路徑**（例如 `/ux-review design/ux/inventory.md`）：只驗證那一份文件
- **`all`**：找出 `design/ux/` 底下所有檔案，逐一驗證
- **`hud`**：專門驗證 `design/ux/hud.md`
- **`patterns`**：專門驗證 `design/ux/interaction-patterns.md`
- **沒有參數**：問使用者要驗證哪一份規格

`all` 的話，先輸出摘要表（檔案 | 結論 | 主要問題），再附上每一份的完整細節。

**每個檔案該用哪份檢查清單**（單一檔案路徑，或 `all` 底下的每個檔案）：看 `/ux-design` 寫入的 `> **Template**:` 標頭行，`UX Spec` → Phase 3A，`HUD Design` → 3B，`Interaction Pattern Library` → 3C。沒有那一行的檔案就用檔名判斷：`hud.md` → 3B，`interaction-patterns.md` → 3C，其他一律 → 3A。報告要寫明假設用了哪份清單，以及為什麼。

---

## Phase 2: Load Cross-Reference Context

驗證任何規格之前，先載入：

1. **Input & Platform 設定**：從 `project.yaml` 讀 `platform` 區塊（`platform.targets`、`platform.primary_input`、`platform.gamepad_support`、`platform.touch_support`）；如果 `project.yaml` 沒有 `platform` 區塊，就退回讀 `.claude/docs/technical-preferences.md` 的 `## Input & Platform` 段落。支援的輸入方式集合這樣取：從 `project.yaml` 讀的話要自己推導，`targets` 有 `PC` 或 `Web` 就算鍵盤／滑鼠；`gamepad_support` 是 Full 或 Partial 就算手把；`touch_support` 是 Full 或 Partial 就算觸控；再加上 `primary_input`。退回 `technical-preferences.md` 的話，就直接用它明列的 Input Methods 欄位。Phase 3A 的 Input Method Coverage 檢查以這個為準，不是規格自己的標頭。兩個來源都沒設定，才退回用規格標頭。
2. `design/accessibility-requirements.md` 裡承諾的無障礙等級（如果檔案存在）
3. `design/ux/interaction-patterns.md` 的 interaction pattern library（如果存在）
4. 規格標頭引用的 GDD（讀它們的 UI Requirements 段落：用 Grep 工具找標題（pattern `^#`，content mode），再用 offset 和 limit 讀那些範圍）
5. `design/player-journey.md` 的玩家旅程地圖（如果存在），用來驗證抵達情境（context-arrival）

---

## Phase 3A: UX Spec Validation Checklist

對以 `ux-spec.md` 為範本的文件跑全部檢查。

### Completeness (required sections)

- [ ] 有文件標頭，含 Status、Author、Platform Target
- [ ] Purpose & Player Need：有玩家視角的需求陳述（不是開發者視角）
- [ ] Player Context on Arrival：描述玩家的狀態和先前做過的事
- [ ] Navigation Position：呈現這個畫面在層級中的位置
- [ ] Entry & Exit Points：所有進入來源和離開去向都有記錄
- [ ] Layout Specification：定義了區域，有 component inventory 表
- [ ] States & Variants：至少記錄 loading、empty/populated、error 三種狀態
- [ ] Interaction Map：涵蓋所有目標輸入方式（看標頭的 platform target）
- [ ] Data Requirements：每個顯示的資料元素都有來源系統和負責人
- [ ] Events Fired：每個玩家動作都有對應事件，或寫明為什麼沒有
- [ ] Transitions & Animations：至少指定進場／退場轉場
- [ ] Input Method Completeness Checklist：Platform Target 那行列出的每種輸入方式各有一個區塊；任何沒勾的項目都要列在 Open Questions 下
- [ ] Accessibility Requirements：有畫面層級的需求
- [ ] Localization Considerations：文字元素有最大字元數
- [ ] Acceptance Criteria：至少 5 條具體可測試的準則

### Quality Checks

**Player Need Clarity**
- [ ] Purpose 是從玩家視角寫的，不是系統／開發者視角
- [ ] 玩家抵達時的目標很明確（「玩家來到這裡是想要 ___」）
- [ ] 玩家抵達時的情境很具體（不是只有「他們打開了背包」）

**Completeness of States**
- [ ] 有記錄 error 狀態（不是只有 happy path）
- [ ] 有記錄 empty 狀態（沒資料的情境）
- [ ] 畫面如果會非同步抓資料，有記錄 loading 狀態
- [ ] 任何有計時器或自動消失的狀態，都有記錄持續時間

**Input Method Coverage**
- [ ] 平台包含 PC：完整規定純鍵盤操作
- [ ] 平台包含主機／手把：記錄了十字鍵導覽和面板按鍵對應
- [ ] 手把上沒有任何互動需要滑鼠等級的精準度
- [ ] 有定義 focus 順序（鍵盤的 Tab 順序、手把的十字鍵順序）

**Data Architecture**
- [ ] 沒有任何資料元素把「UI」列為負責人（UI 不可以擁有遊戲狀態）
- [ ] 所有即時資料都有指定更新頻率（不是只寫「realtime」，要寫什麼會觸發更新）
- [ ] 所有資料元素都有指定 null 處理（資料不可用時顯示什麼？）

**Accessibility**
- [ ] 符合或超過 `accessibility-requirements.md` 的無障礙等級
- [ ] Basic 等級：沒有只靠顏色傳達的資訊指示
- [ ] Standard 等級以上：有記錄 focus 順序，有指定文字對比度
- [ ] Comprehensive 等級以上：關鍵狀態變化有螢幕閱讀器播報
- [ ] 色盲檢查：任何用顏色編碼的元素都有非顏色的替代方式

**GDD Alignment**
- [ ] 標頭引用的每條 GDD UI Requirement，這份規格都有處理
- [ ] 沒有任何 UI 元素在沒有對應 GDD 需求的情況下顯示或修改遊戲狀態
- [ ] 沒有任何 GDD UI Requirement 在這份規格裡缺漏（對照檢查引用的 GDD 段落）

**Pattern Library Consistency**
- [ ] 所有互動元件都引用 pattern library（或註明它們是新 pattern）
- [ ] pattern library 已經有的 pattern 行為，沒有從頭重新規定
- [ ] 這份規格裡新發明的 pattern 都有標記要加進 pattern library

**Localization**
- [ ] 所有文字量大的元素都有字元數上限警告
- [ ] 任何會影響版面的文字，都有標記要預留 40% 的擴充空間

**Acceptance Criteria Quality**
- [ ] 準則夠具體，沒看過設計文件的 QA 測試人員也能照著測
- [ ] 有效能準則（畫面在 X ms 內開啟）
- [ ] 有解析度準則
- [ ] 沒有任何準則需要讀另一份文件才能評估

---

## Phase 3B: HUD Validation Checklist

對以 `hud-design.md` 為範本的文件跑全部檢查。

### Completeness

- [ ] 有定義 HUD Philosophy
- [ ] Information Architecture 表涵蓋 GDD 裡所有有 UI Requirements 的系統
- [ ] Layout Zones 已定義，且所有目標平台都有 safe zone 邊界
- [ ] 每個 HUD 元素都有完整規格（區域、顯示觸發條件、資料來源、優先級）
- [ ] HUD States by Gameplay Context 至少涵蓋：探索、戰鬥、對話／過場、暫停
- [ ] Information Hierarchy 給每個 HUD 元素一個優先等級（MUST KEEP / SHOULD KEEP / CAN HIDE / ALWAYS HIDE）
- [ ] 有定義 Visual Budget（同時顯示元素數上限、畫面佔比上限）
- [ ] Platform Adaptation 涵蓋所有目標平台
- [ ] 玩家可調整的元素有 Tuning Knobs
- [ ] Acceptance Criteria：至少 5 條具體可測試的準則

### Quality Checks

- [ ] 沒有任何 HUD 元素遮住畫面中央的遊玩區，除非有可見性規則把它藏起來
- [ ] 任何 GDD 裡存在的每項資訊，不是出現在 HUD，就是明確歸類為「hidden/demand」
- [ ] 所有用顏色編碼的 HUD 元素都有色盲版本
- [ ] Feedback & Notification 段落裡的 HUD 元素有定義 queue／優先級行為
- [ ] 符合 Visual Budget：同時顯示的元素總數在預算內

### GDD Alignment

- [ ] `design/gdd/systems-index.md` 裡屬於 UI 類別的所有系統，在 HUD 都有呈現（或有正當的缺席理由）

---

## Phase 3C: Pattern Library Validation Checklist

- [ ] Pattern 目錄索引是最新的（和文件裡實際的 pattern 一致）
- [ ] 所有標準控制項 pattern 都有規格：button 變體、toggle、slider、dropdown、list、grid、modal、dialog、toast、tooltip、progress bar、input field、tab bar、scroll
- [ ] 目前 UX 規格需要的所有遊戲專屬 pattern 都存在
- [ ] 每個 pattern 都有：When to Use、When NOT to Use、完整狀態規格、無障礙規格、實作備註
- [ ] 有 Animation Standards 表
- [ ] 有 Sound Standards 表
- [ ] pattern 之間沒有行為衝突（例如「返回」行為在所有導覽 pattern 都一致）

---

## Phase 4: Output the Verdict

```markdown
## UX Review: [Document Name]
**Date**: [date]
**Reviewer**: ux-review skill
**Document**: [file path]
**Checklist**: [3A / 3B / 3C — from its Template line, or assumed from the file name]
**Platform Target**: [from header]
**Accessibility Tier**: [from header or accessibility-requirements.md]

### Completeness: [X/Y sections present]
- [x] Purpose & Player Need
- [ ] States & Variants — MISSING: error state not documented

### Quality Issues: [N found]
1. **[Issue title]** [BLOCKING / ADVISORY]
   - What's wrong: [specific description]
   - Where: [section name]
   - Fix: [specific action to take]

### GDD Alignment: [ALIGNED / GAPS FOUND]
- GDD [name] UI Requirements — [X/Y requirements covered]
- Missing: [list any uncovered GDD requirements]

### Accessibility: [COMPLIANT / GAPS / NON-COMPLIANT / NOT ASSESSED]
- Target tier: [tier]
- [list specific accessibility findings]

> **如果 `design/accessibility-requirements.md` 不存在，就沒有已承諾的等級，這個維度也就沒有準則。** 回報
> `Accessibility: NOT ASSESSED — no committed tier (design/accessibility-requirements.md absent)`，
> 絕對不要回報成 COMPLIANT：拿一個不存在的標準去比對的關卡，就像永遠不會失敗的 assertion 一樣，一定會過。同樣的規則在
> `/team-ui` Phase 4 也有，這裡照抄一份，避免兩邊漂移。如果規格自己的標頭有寫等級，就當作**假設**帶下去，並且明說那是假設、不是已承諾的。建議跑 `/ux-design accessibility` 來定下等級。

### Pattern Library: [CONSISTENT / INCONSISTENCIES FOUND / N/A]
- [findings]

> **HUD 設計沒有可以拿來比對的 Pattern Library 檢查清單（Phase 3B 沒有），所以 Pattern Library 是 N/A，不算進維度數量。**
> 回報 `Pattern Library: N/A — no pattern library checklist for this document
> type`。
>
> UX 規格的這個維度有檢查清單，要拿 `design/ux/interaction-patterns.md` 來比對。如果那個檔案不存在：只有在 workflow tier 不要求這個 library 時（`minimal`）才算 N/A，回報
> `Pattern Library: N/A — interaction pattern library not required at this
> tier`。在要求或建議使用它的 tier（`standard`、`full`），改回報
> `Pattern Library: NOT ASSESSED — design/ux/interaction-patterns.md not found`：
> library 是缺了，不是不在範圍內，而 NOT ASSESSED 會把它當成未解決的項目算進結論裡。

### Verdict: APPROVED / NOT ASSESSED / NEEDS REVISION / MAJOR REVISION NEEDED
**Blocking issues**: [N] — must be resolved before implementation
**Advisory issues**: [N] — recommended but not blocking
**Dimensions not assessed**: [N] — [name each, and what would make it checkable]

[For APPROVED]: This spec is ready for handoff to `/team-ui` Phase 2
(Visual Design).

[For NOT ASSESSED]: [N] of the four review dimensions could not be evaluated:
[name them]. The spec may well be sound — this review cannot say either way for
those dimensions. [For each: the one input that would make it checkable.]
Handoff to `/team-ui` is not recommended on this result.

[For NEEDS REVISION]: Address the [N] blocking issues above, then re-run
`/ux-review`.

[For MAJOR REVISION NEEDED]: The spec has fundamental gaps in [areas].
Recommend returning to `/ux-design` to rework [sections].
```

---

## Phase 5: Collaborative Protocol

這個 skill 是唯讀的：絕對不編輯或寫入任何檔案，只回報發現。

給出結論之後：
- **APPROVED**：建議跑 `/team-ui` 開始協調實作
- **NOT ASSESSED**：逐個維度指出缺少的輸入，並主動幫忙產出（無障礙等級沒定就用 `/ux-design accessibility`，沒有 UI requirements 就給 GDD 路徑）。不要在同樣缺輸入的情況下重跑審查然後給出不同結論，只有新的輸入才能改變這個結論
- **NEEDS REVISION**：主動提議幫忙補具體缺口（「要我幫你起草缺的 error 狀態嗎？」），但不要自動修，等使用者指示
- **MAJOR REVISION NEEDED**：建議回到 `/ux-design`，並指出要重做的段落

絕對不要擋使用者往下走，結論只是建議。記錄風險、呈現發現，讓使用者自己決定要不要在有疑慮的情況下繼續。使用者如果選擇帶著 NEEDS REVISION 的規格往下走，就是自己承擔已記錄的風險。
