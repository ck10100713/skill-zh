---
name: "tw-ecom-logistics-cross-border"
description: "為台灣選擇貨運業者並管理跨境運送作業：業者選擇（DHL / FedEx / UPS / 郵局 國際）、通關作業（報關）、DDP vs DDU 的取捨、運單產生，以及退貨處理。當要選業者、估算運費或運送時間，或管理跨境貨物的實體流動時使用。關稅/稅金計算、HS code 分類或境外電商稅務登記「不要」用這個（看 tw-ecom-compliance-cross-border）。台灣國內運送也「不要」用這個。STATUS: SKELETON — 內文待補。"
metadata:
  category: "WP-01 電商"
  domain: "ecommerce-tw"
  layer: "logistics"
  related_mcps: []
  related_skills: ["tw-ecom-compliance-cross-border", "xborder-logistics", "xborder-sea-entry"]
  last_verified: "2026-04"
  status: "skeleton"
  tags: ["taiwan", "logistics", "cross-border"]
---

# 跨境物流

> **STATUS: SKELETON**：內文待補。

## 何時使用這個 skill

- 為 台灣 → 海外 或 海外 → 台灣 的貨件選業者
- 估算運費、運送時間，或 DDP 的完稅總成本
- 管理通關作業（報關）和文件準備
- 處理海外買家的退貨
- 針對特定航線比較 DHL / FedEx / UPS / 郵局 國際

## 何時「不要」使用

- 關稅/稅金計算、HS code 分類或報單申報 → `tw-ecom-compliance-cross-border`
- 境外電商銷售稅登記 → `tw-ecom-compliance-cross-border`
- 台灣國內物流 → `tw-ecom-logistics-home` / `tw-ecom-logistics-cvs`

## 核心概念

TODO: DDP vs DDU 的取捨（完稅成本透明度、責任轉移）、業者選擇框架（重量 / 速度 / 目的地 / DDP 能力）、通關文件準備（商業發票、包裝明細、原產地證明）、各業者的運單標準、退貨的阻力與成本結構。NOTE: HS code 分類、免稅額門檻，以及關稅/營業稅稅率屬於 `tw-ecom-compliance-cross-border`，不要在這裡重複。

## 決策樹

TODO: 依目的地 / 重量 / 速度 / DDP 偏好來選業者。

## 實作指引

TODO: 通關文件準備、運單產生、追蹤對帳。

## 常見陷阱

TODO: 5-6 個陷阱（HS 分類錯誤、DDP 總成本衝擊、退貨黑洞、禁運品清單、自由貿易港區 vs 一般海關）。

## IRON LAW

TODO.

## 輸出格式

TODO.

## 相關

- `tw-ecom-compliance-cross-border`
- `xborder-logistics`, `xborder-sea-entry`

_Last verified: 2026-04_
