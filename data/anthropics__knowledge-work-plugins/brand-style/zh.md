---
name: brand-style
description: >
  設定並更新老闆的品牌外觀與輸出偏好，plugin 產出的每一頁、每份文件之後都會自動照這套走。
  品牌資訊從貼上的網站連結或一段白話描述取得，絕對不要求色碼、色盤或上傳檔案。
  先在範例頁面上預覽，再問他們想怎麼收到輸出（視覺化 artifact、Word 文件、markdown、Notion 頁面、
  Canva Docs，或每個 skill 自己挑最適合的），然後把兩者都存進 business profile。
  第一次設定時在 smb-onboard 裡執行，之後可以單獨使用。
  當老闆說「更新我的品牌」「我們改版了」「換我的顏色」「讓報告配合我們的新風格」
  「改一下你給我報告的方式」「我想要 Word 文件」，或任何跟 plugin 交給他們的內容外觀或格式有關的話時使用。
allowed-tools: Read, WebFetch
---

# Brand Style

老闆在這裡統一控制所有東西長什麼樣子、用什麼方式交付。onboarding 時設定一次，之後隨時用一句話就能改。

## Step 1 — 顯示目前的設定

讀 `## Business context` 區塊。如果已經有 Brand colors、Logo 或 Output preference，先用白話講回去：「你現在的頁面是深綠配米色，加上葉子 logo，你拿到的是視覺化頁面。這次要改什麼？」只想改一項的老闆，不該把其他項目重答一遍。

如果還什麼都沒存（第一次執行，通常是在 `smb-onboard` 裡），直接跳到擷取。

## Step 2 — 無摩擦地擷取品牌

兩條路，老闆幾乎都不用花力氣：

- **網站連結。** 用 WebFetch 抓網站，取出 logo URL、主要品牌色（從 CSS、theme 或社群預覽圖）和標語。老闆只要貼連結，其他都不用做。做法參考
  [`../smb-onboard/reference/website-research.md`](../smb-onboard/reference/website-research.md)。
- **白話描述。**「森林綠配米色」「海軍藍配暖灰」「像現代律師事務所那種」。把這些話自己轉成實際的顏色。

**絕對不要問色碼、色盤或檔案上傳。** 品牌設定只需要貼一個連結或講一句話，不要更多。「跳過」永遠是合法答案，代表用乾淨的預設風格。

## Step 3 — 存之前先預覽

用 house style（`../../shared/artifact-style.md`）把候選品牌套到一個小型範例頁面，輸出成 HTML artifact：一個標題、一個數字卡、一張短表格、一個狀態標籤。這樣老闆看到的是真實元件上的效果，不是一塊色票。只問一個問題：「符合嗎？」

如果他們要調整（「綠色深一點」「米色少一點」），就套用後重新預覽。這個迴圈成本很低，之後每一頁都套錯品牌的代價可不低。

## Step 4 — 問輸出要怎麼送達

六選一，用選擇題呈現（如果老闆只是來改顏色，而且偏好已經存過，就跳過）：

1. **視覺化 artifact** — 在這裡直接看的樣式頁面（預設）
2. **Word 文件** — 可下載的 DOCX 檔
3. **Markdown** — 可下載的純 .md 檔
4. **Notion** — 建在他們 Notion 工作區的頁面（需要 Notion connector，問他們要放在工作區的哪裡）
5. **Canva** — 建在他們 Canva 帳號的 Canva Docs（需要 Canva connector；如果已連線，執行 `list-brand-kits`，問一次要套用哪個 brand kit 或不套用；如果沒連線，由第一個要交付到 Canva 的 skill 來問）
6. **Best for the skill** — 每個 skill 自己挑適合工作性質的格式

答案要原樣存成下列其中一個：`visual artifacts`、`docx`、`md`、`notion`、`canva`、`best for skill`。如果他們選了 Notion 或 Canva，但那個 connector 還沒連線，照樣存，並說明在連線之前交付物會退回成視覺化 artifact，然後主動提議幫忙連線。

## Step 5 — 存檔，要先取得同意

把要存的東西秀出來：Website、Brand colors、Logo、Output preference，偏好是 Canva 的話還要加上 Canva brand kit（名稱和 id），然後等對方說好。接著只更新 `## Business context` 區塊裡這些欄位，欄位名稱要完全照
[`../smb-onboard/reference/onboard-checklist.md`](../smb-onboard/reference/onboard-checklist.md)。
其他欄位絕對不碰，也絕對不要默默覆蓋。

收尾講效果，不講機制：「好了，從現在起每一頁、每份文件都會用新的風格。」

## 不要做的事

- **不要問色碼、色盤或上傳檔案。** 永遠只要一個連結或一句話。
- **不要把整套訪談重跑一遍。** 這個 skill 只改外觀和交付方式，其他都不動。說「更新我的品牌」的老闆，不是要再 onboard 一次。
- **沒有預覽和對方點頭就不要存。** 會套用到之後每一頁的品牌，值得一次確認。
- **不要幫舊的交付物換風格。** 變更只從現在開始生效，絕對不要宣稱過去的文件也更新了。

## 更新之後

用一句話講改了什麼。自然的下一步是看實際效果：主動提議「Monday brief」（`/monday-brief`）或「生意現在怎麼樣？」（`business-pulse`），讓第一張套用新品牌的頁面馬上出現。提議不超過三個，這個 session 裡被拒絕過的不要再提。
