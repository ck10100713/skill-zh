---
name: evm-token-decimals
description: 預防跨 EVM 鏈默默發生的 decimal 不一致 bug。涵蓋 runtime 查詢 decimal、感知鏈的快取、橋接代幣的精度漂移，以及給 bot、dashboard 和 DeFi 工具用的安全正規化。在處理跨 EVM 鏈的代幣數量，或餘額、價格、轉帳金額差了好幾個數量級時使用。
metadata:
  version: "1.0.0"
  origin: ECC direct-port adaptation
---

# EVM 代幣 Decimals

默默發生的 decimal 不一致，是最容易讓你出貨的餘額或 USD 價值差了好幾個數量級、卻完全不報錯的原因之一。

## 何時使用

- 在 Python、TypeScript 或 Solidity 中讀取 ERC-20 餘額
- 從鏈上餘額計算法幣價值
- 比較多條 EVM 鏈上的代幣數量
- 處理橋接過來的資產
- 建立投資組合追蹤器、bot 或聚合器

## 運作方式

絕對不要假設穩定幣在每個地方用的 decimals 都一樣。在 runtime 查詢 `decimals()`，用 `(chain_id, token_address)` 當 key 做快取，並在價值計算上用 decimal 安全的數學。

## 範例

### 在 runtime 查詢 decimals

```python
from decimal import Decimal
from web3 import Web3

ERC20_ABI = [
    {"name": "decimals", "type": "function", "inputs": [],
     "outputs": [{"type": "uint8"}], "stateMutability": "view"},
    {"name": "balanceOf", "type": "function",
     "inputs": [{"name": "account", "type": "address"}],
     "outputs": [{"type": "uint256"}], "stateMutability": "view"},
]

def get_token_balance(w3: Web3, token_address: str, wallet: str) -> Decimal:
    contract = w3.eth.contract(
        address=Web3.to_checksum_address(token_address),
        abi=ERC20_ABI,
    )
    decimals = contract.functions.decimals().call()
    raw = contract.functions.balanceOf(Web3.to_checksum_address(wallet)).call()
    return Decimal(raw) / Decimal(10 ** decimals)
```

不要寫死 `1_000_000`，因為同一個符號在別的地方通常有 6 位 decimals。

### 依鏈與代幣做快取

```python
from functools import lru_cache

@lru_cache(maxsize=512)
def get_decimals(chain_id: int, token_address: str) -> int:
    w3 = get_web3_for_chain(chain_id)
    contract = w3.eth.contract(
        address=Web3.to_checksum_address(token_address),
        abi=ERC20_ABI,
    )
    return contract.functions.decimals().call()
```

### 防禦式處理特殊代幣

```python
try:
    decimals = contract.functions.decimals().call()
except Exception:
    logging.warning(
        "decimals() reverted on %s (chain %s), defaulting to 18",
        token_address,
        chain_id,
    )
    decimals = 18
```

記錄 fallback 並讓它保持可見。舊的或不標準的代幣仍然存在。

### 在 Solidity 中正規化成 18 位 decimal 的 WAD

```solidity
interface IERC20Metadata {
    function decimals() external view returns (uint8);
}

function normalizeToWad(address token, uint256 amount) internal view returns (uint256) {
    uint8 d = IERC20Metadata(token).decimals();
    if (d == 18) return amount;
    if (d < 18) return amount * 10 ** (18 - d);
    return amount / 10 ** (d - 18);
}
```

### 搭配 ethers 的 TypeScript

```typescript
import { Contract, formatUnits } from 'ethers';

const ERC20_ABI = [
  'function decimals() view returns (uint8)',
  'function balanceOf(address) view returns (uint256)',
];

async function getBalance(provider: any, tokenAddress: string, wallet: string): Promise<string> {
  const token = new Contract(tokenAddress, ERC20_ABI, provider);
  const [decimals, raw] = await Promise.all([
    token.decimals(),
    token.balanceOf(wallet),
  ]);
  return formatUnits(raw, decimals);
}
```

### 快速的鏈上檢查

```bash
cast call <token_address> "decimals()(uint8)" --rpc-url <rpc>
```

## 規則

- 一律在 runtime 查詢 `decimals()`
- 依鏈加代幣地址做快取，不要用符號
- 用 `Decimal`、`BigInt` 或等價的精確數學，不要用 float
- 橋接或 wrapper 變更之後，重新查詢 decimals
- 比較或定價之前，先一致地正規化內部帳務
