---
name: "tw-ecom-compliance-pdpa"
description: "電商專用的個資法（PDPA）合規：註冊時的會員同意、cookie 同意、訂單 / 付款資料保存、DSAR（資料當事人存取請求）處理，以及台灣商家的跨境資料傳輸。當要建置台灣電商的註冊 / CRM 流程、回應會員資料請求，或稽核 cookie 時使用。一般性的個資法 / GDPR 基礎請看 `law-gdpr-pdpa`。STATUS: SKELETON — 內文待補。"
metadata:
  category: "WP-05 台灣創業"
  domain: "ecommerce-tw"
  layer: "compliance"
  related_mcps: []
  related_skills: ["law-gdpr-pdpa", "tw-ecom-compliance-consumer", "tw-ecom-operations-line-oa"]
  last_verified: "2026-04"
  status: "skeleton"
  tags: ["taiwan", "compliance", "pdpa", "privacy"]
---

# 電商個資法合規

> **STATUS: SKELETON**：內文待補。

## 何時使用這個 skill

- 設計台灣商店的會員註冊同意流程
- 為台灣流量建置 cookie 同意橫幅
- 回應 DSAR（居民的資料當事人存取請求）
- 設計訂單 / 付款資料的保存政策
- 跨境傳輸（台灣 → AWS US / GCP APAC）

## 何時「不要」使用

- 一般性的個資法 / GDPR 概念 → `law-gdpr-pdpa`
- LINE OA 的行銷同意 → `tw-ecom-operations-line-oa`

## 核心概念

TODO: 個資法 §5 特定目的原則、第八條 告知義務、蒐集 vs 處理 vs 利用 的區分。

## 決策樹

TODO: 資料流 → 同意表單設計。

## 實作指引

TODO: 同意表單範本、DSAR SOP、保存期限表、跨境傳輸評估。

## 常見陷阱

TODO: 5-6 個陷阱（opt-in 與 opt-out 搞混、第三方嵌入造成外洩、員工存取紀錄、資料外洩 72 小時通報）。

## IRON LAW

TODO.

## 輸出格式

TODO.

## 相關

- `law-gdpr-pdpa`
- `tw-ecom-operations-line-oa`

_Last verified: 2026-04_
