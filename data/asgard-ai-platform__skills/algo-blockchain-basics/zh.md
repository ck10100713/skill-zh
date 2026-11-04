---
name: "algo-blockchain-basics"
description: "說明區塊鏈的基礎，包含分散式帳本架構、共識機制和區塊結構。當使用者需要理解區塊鏈概念、評估區塊鏈適不適合某個使用情境，或設計以區塊鏈為基礎的方案時使用，即使他們說的是『how does blockchain work』『do I need blockchain』或『distributed ledger』。"
metadata:
  category: "WP-49 區塊鏈演算法"
  tags: ["blockchain", "distributed-ledger", "consensus", "cryptography"]
---

# 區塊鏈基礎

## 概述

區塊鏈是一種分散式、只能附加的帳本，交易區塊之間用密碼學連結。每個區塊包含：交易、前一個區塊的 hash、時間戳記和 nonce。共識機制（PoW、PoS、BFT）讓大家不需要中央機構也能達成一致。代價是：去中心化 vs 效能。

## 何時使用

**觸發條件：**
- 評估區塊鏈適不適合某個使用情境
- 設計需要分散式信任、不可竄改或透明度的系統
- 為了整合或開發而理解區塊鏈架構

**不該使用的情況：**
- 已經有一個可信任、運作良好的中央機構時（用資料庫）
- 主要需求是效能（每秒數千筆 TPS）時
- 資料隱私要求必須能刪除時（區塊鏈只能附加）

## 演算法

```
IRON LAW: Blockchain Is Useful ONLY When You Need TRUSTLESS Consensus
If participants trust each other (or trust a central authority), a
traditional database is faster, cheaper, and simpler. Blockchain's
value proposition is: untrusted parties can agree on state without
an intermediary. If trust already exists, blockchain adds overhead
with no benefit. Ask: "Who doesn't trust whom?" before choosing blockchain.
```

### 階段 1：輸入驗證
用區塊鏈的決策準則來評估使用情境：有多個互不信任的寫入者嗎？需要不可竄改嗎？沒有可信任的中央方嗎？需要公開可驗證嗎？
**關卡：** 4 項準則至少滿足 3 項，才有理由用區塊鏈。

### 階段 2：核心演算法
**區塊結構：**
1. 交易被分組成區塊
2. 每個區塊 header 包含：前一個 hash、交易的 Merkle root、時間戳記、nonce
3. 區塊 header 的 hash 把它連到前一個區塊（鏈）
4. 修改任何一個過去的區塊，會讓後面所有的 hash 失效

**共識機制：**
- PoW（Proof of Work）：礦工競爭解 hash 謎題。耗能、安全。
- PoS（Proof of Stake）：驗證者質押代幣。省能源，靠經濟誘因運作。
- BFT（Byzantine Fault Tolerance）：投票制，最終確定性快，需要已知的驗證者集合。

### 階段 3：驗證
檢查：這個使用情境是不是真的有多方且存在信任缺口？有沒有更簡單的方案（共用資料庫、數位簽章）就夠了？
**關卡：** 區塊鏈有正當理由，且選好合適的共識機制。

### 階段 4：輸出
回傳架構建議，附上取捨分析。

## 輸出格式

```json
{
  "recommendation": {"use_blockchain": true, "type": "permissioned", "consensus": "PBFT", "platform": "Hyperledger Fabric"},
  "trade_offs": {"decentralization": "medium", "throughput_tps": 3000, "finality_seconds": 2, "energy": "low"},
  "metadata": {"use_case": "supply chain provenance", "participants": 5, "trust_level": "low"}
}
```

## 範例

### 輸入輸出範例
**輸入：** 5 家公司追蹤海鮮從漁船到餐廳的來源
**預期：** 建議用許可制區塊鏈（參與者已知、彼此不信任、需要不可竄改的稽核軌跡）。平台：Hyperledger Fabric 或類似的。

### 邊界情況
| 輸入 | 預期 | 原因 |
|-------|----------|-----|
| 單一公司內部使用 | 不要用區塊鏈 | 內部本來就有信任 |
| 需要刪除資料（GDPR） | 區塊鏈有問題 | 不可竄改和被遺忘權衝突 |
| 需要公開透明 | 公有鏈 / 聯盟鏈 | 非許可制或混合式 |

## 注意事項

- **區塊鏈 ≠ 加密貨幣**：區塊鏈是技術，加密貨幣只是其中一種應用。很多區塊鏈的使用情境跟代幣毫無關係。
- **不可竄改是一個光譜**：「許可制」區塊鏈可以靠聯盟協議改寫。真正的不可竄改只存在於大型公有鏈。
- **Oracle 問題**：區塊鏈保證「鏈上」資料的完整性，但無法保證從真實世界「進入」鏈上的資料是否準確。垃圾進，就是不可竄改的垃圾。
- **可擴展性三難**：去中心化、安全、可擴展，三選二。沒有任何區塊鏈能同時把三個都做到最好。
- **法規不確定性**：區塊鏈紀錄、智能合約和代幣的法律地位因司法管轄區而異。正式上線前要先諮詢法務。

## 參考資料

- 共識機制比較，見 `references/consensus-comparison.md`
- 區塊鏈決策框架，見 `references/decision-framework.md`
