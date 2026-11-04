---
name: "algo-blockchain-smart-contract"
description: "設計並實作智能合約，也就是在區塊鏈上自動執行的程式化協議。當使用者需要建立自動化的鏈上邏輯、評估智能合約安全性，或設計代幣化的商業規則時使用，即使他們說的是『smart contract development』『automated agreement』或『on-chain logic』。"
metadata:
  category: "WP-49 區塊鏈演算法"
  tags: ["blockchain", "smart-contract", "solidity", "defi"]
---

# 智能合約

## 概述

智能合約是儲存在區塊鏈上、自動執行的程式，條件一滿足就自動強制執行協議條款。主要用 Solidity（Ethereum/EVM）或 Rust（Solana）撰寫。一旦部署，程式碼就不可更改，bug 沒辦法 patch，只能遷移。安全性至關重要，因為被攻擊的損失無法挽回。

## 何時使用

**觸發條件：**
- 自動化多方協議，不需要中間人就能執行
- 建立以代幣為基礎的系統（NFT、DeFi、治理）
- 在鏈上建立透明、可稽核的商業邏輯

**不該使用的情況：**
- 單純的 CRUD 操作（用資料庫）
- 商業邏輯常常改動時（不可更改讓更新成本很高）
- 主要輸入是鏈下資料時（依賴 oracle 有風險）

## 演算法

```
IRON LAW: Deployed Smart Contracts Are IMMUTABLE — Bugs Are Permanent
Once deployed, contract code cannot be changed. A bug that loses funds
is IRREVERSIBLE. There is no "hotfix" or "rollback" (unless the
contract includes an upgrade proxy pattern). Security audit BEFORE
deployment is not optional — it is the only protection.
```

### 階段 1：輸入驗證
定義：合約目的、參與者、條件、狀態變數、存取控制。判斷：哪些邏輯「一定」要在鏈上、哪些可以放在鏈下。
**關卡：** 商業邏輯已明確規格化，並說明了為什麼需要上鏈。

### 階段 2：核心演算法
**設計：**
1. 定義狀態變數（儲存在鏈上，要花 gas）
2. 定義函式：external（使用者可呼叫）、internal（輔助邏輯）
3. 實作存取控制（onlyOwner、role-based、multisig）
4. 處理邊界情況：reentrancy guard、整數溢位檢查、gas 上限

**安全模式：**
- Checks-Effects-Interactions（防止 reentrancy）
- 付款用 pull 而不是 push
- 鏈上資料越少越好（存 hash，不存完整資料）
- 可升級的 proxy 模式（需要可變動時）

### 階段 3：驗證
測試：unit test 涵蓋所有路徑、邊界情況、違反存取控制的情形。安全稽核：自動化（Slither、Mythril）+ 人工審查。先部署到 testnet。
**關卡：** 所有測試通過、自動化安全掃描沒有問題、testnet 部署成功。

### 階段 4：輸出
回傳合約設計，附上安全分析。

## 輸出格式

```json
{
  "contract": {"name": "Escrow", "functions": 5, "state_variables": 4, "access_roles": ["buyer", "seller", "arbiter"]},
  "security": {"audit_status": "passed", "patterns_used": ["checks_effects_interactions", "pull_payment"], "known_risks": ["oracle_dependency"]},
  "metadata": {"platform": "ethereum", "language": "solidity", "estimated_gas": 250000}
}
```

## 範例

### 輸入輸出範例
**輸入：** Escrow 合約：買方存款、賣方交貨、仲裁者處理爭議
**預期：** 合約包含 deposit()、confirmDelivery()、dispute()、withdraw() 函式。資金會被扣住，直到條件滿足。

### 邊界情況
| 輸入 | 預期 | 原因 |
|-------|----------|-----|
| Gas 價格飆升 | 交易可能失敗或變貴 | 一定要設 gas 上限並處理失敗 |
| Reentrant 呼叫 | 一定要擋掉 | Reentrancy 是智能合約漏洞的第一名 |
| 需要升級合約 | 用 proxy 模式或遷移 | 預設就是不可更改 |

## 注意事項

- **Reentrancy 攻擊**：The DAO 事件（損失 $60M）就是利用 reentrancy。一定要用 Checks-Effects-Interactions 模式和（或）ReentrancyGuard。
- **整數溢位 / 下溢**：Solidity 0.8+ 內建溢位檢查，更早的版本要用 SafeMath 函式庫。永遠不要假設算術是安全的。
- **Front-running**：礦工 / 驗證者看得到待處理的交易，可以先插入自己的交易（MEV）。敏感操作需要 commit-reveal 機制。
- **Gas 最佳化**：每個操作都要花 gas。盡量減少 storage 寫入（最貴）、不需要在鏈上查詢的資料用 event、把變數打包。
- **可升級 vs 不可更改**：Proxy 模式允許升級，但會增加複雜度和信任假設（誰可以升級？）。依信任模型來選。
- **Oracle 依賴**：智能合約無法直接存取鏈下資料。Oracle（Chainlink 等）會帶來信任假設。Oracle 被攻破，合約就跟著被攻破。

## 參考資料

- 常見的漏洞模式，見 `references/vulnerability-patterns.md`
- Gas 最佳化技巧，見 `references/gas-optimization.md`
