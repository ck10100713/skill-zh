---
name: ads-launch
description: "透過 Claude Ads 有 capability 把關的 adapter，起草或在明確指示下執行付費廣告活動上線。適用於建立廣告活動、上線計畫、發布廣告、啟用廣告活動、上傳創意，或要求把廣告活動推上線。"
---

# 廣告活動上線

預設用 `--draft`。

1. 載入驗證過的 setup 設定檔、帳號 snapshot、廣告活動計畫、創意 manifest、平台 capability manifest、政策 findings 和追蹤檢查。
2. 草稿如果缺少帳號/物件範圍、目標、轉換、預算、日期、受眾鎖定、素材、目的地、衡量或政策資格，就拒絕。
3. 產生確定性的 mutation plan，包含確切提議的物件、前後狀態、影響範圍、對學習的影響、負責人、成功衡量、驗證窗口、idempotency key、稽核去處和 rollback。
4. 用 `--apply` 時，要求這項確切的操作已啟用且經過獨立測試，然後針對這份確切的計畫取得明確核准。
5. 套用最小且可逆的變更，驗證遠端狀態，並保存不可變更的稽核與 rollback 紀錄。

缺少上限、帳號狀態過期、遠端狀態改變、追蹤不完整、政策審查未通過，或 adapter 不可用，都會擋下 apply。不支援永久刪除。
