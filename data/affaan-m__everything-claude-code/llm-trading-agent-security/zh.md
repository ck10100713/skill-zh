---
name: llm-trading-agent-security
description: 針對擁有錢包或交易權限的自主交易 agent 的安全模式，涵蓋 prompt injection、花費上限、送出前模擬、circuit breaker、MEV 防護與金鑰處理。在自主 agent 持有錢包或交易權限，且需要檢視其上限、模擬或金鑰處理時使用。
metadata:
  version: "1.0.0"
  origin: ECC direct-port adaptation
---

# LLM 交易 Agent 安全

自主交易 agent 的威脅模型比一般 LLM 應用嚴酷得多：一次 injection 或一條壞掉的工具路徑，就能直接變成資產損失。

## 何時使用

- 建構會簽署並送出交易的 AI agent
- 稽核交易機器人或鏈上執行助理
- 為 agent 設計錢包金鑰管理
- 讓 LLM 能下單、swap 或操作資金庫

## 運作方式

把防禦分層。沒有任何單一檢查是足夠的。把 prompt 衛生、花費政策、模擬、執行上限與錢包隔離視為彼此獨立的控制。

## 範例

### 把 prompt injection 當成金融攻擊

```python
import re

INJECTION_PATTERNS = [
    r'ignore (previous|all) instructions',
    r'new (task|directive|instruction)',
    r'system prompt',
    r'send .{0,50} to 0x[0-9a-fA-F]{40}',
    r'transfer .{0,50} to',
    r'approve .{0,50} for',
]

def sanitize_onchain_data(text: str) -> str:
    for pattern in INJECTION_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            raise ValueError(f"Potential prompt injection: {text[:100]}")
    return text
```

不要不加檢查就把 token 名稱、交易對標籤、webhook 或社群 feed 塞進具備執行能力的 prompt。

### 硬性花費上限

```python
from decimal import Decimal

MAX_SINGLE_TX_USD = Decimal("500")
MAX_DAILY_SPEND_USD = Decimal("2000")

class SpendLimitError(Exception):
    pass

class SpendLimitGuard:
    def check_and_record(self, usd_amount: Decimal) -> None:
        if usd_amount > MAX_SINGLE_TX_USD:
            raise SpendLimitError(f"Single tx ${usd_amount} exceeds max ${MAX_SINGLE_TX_USD}")

        daily = self._get_24h_spend()
        if daily + usd_amount > MAX_DAILY_SPEND_USD:
            raise SpendLimitError(f"Daily limit: ${daily} + ${usd_amount} > ${MAX_DAILY_SPEND_USD}")

        self._record_spend(usd_amount)
```

### 送出前先模擬

```python
class SlippageError(Exception):
    pass

async def safe_execute(self, tx: dict, expected_min_out: int | None = None) -> str:
    sim_result = await self.w3.eth.call(tx)

    if expected_min_out is None:
        raise ValueError("min_amount_out is required before send")

    actual_out = decode_uint256(sim_result)
    if actual_out < expected_min_out:
        raise SlippageError(f"Simulation: {actual_out} < {expected_min_out}")

    signed = self.account.sign_transaction(tx)
    return await self.w3.eth.send_raw_transaction(signed.raw_transaction)
```

### Circuit Breaker

```python
class TradingCircuitBreaker:
    MAX_CONSECUTIVE_LOSSES = 3
    MAX_HOURLY_LOSS_PCT = 0.05

    def check(self, portfolio_value: float) -> None:
        if self.consecutive_losses >= self.MAX_CONSECUTIVE_LOSSES:
            self.halt("Too many consecutive losses")

        if self.hour_start_value <= 0:
            self.halt("Invalid hour_start_value")
            return

        hourly_pnl = (portfolio_value - self.hour_start_value) / self.hour_start_value
        if hourly_pnl < -self.MAX_HOURLY_LOSS_PCT:
            self.halt(f"Hourly PnL {hourly_pnl:.1%} below threshold")
```

### 錢包隔離

```python
import os
from eth_account import Account

private_key = os.environ.get("TRADING_WALLET_PRIVATE_KEY")
if not private_key:
    raise EnvironmentError("TRADING_WALLET_PRIVATE_KEY not set")

account = Account.from_key(private_key)
```

使用專用的 hot wallet，只放必要的 session 資金。絕對不要讓 agent 指向主要的資金庫錢包。

### MEV 與期限保護

```python
import time

PRIVATE_RPC = "https://rpc.flashbots.net"
MAX_SLIPPAGE_BPS = {"stable": 10, "volatile": 50}
deadline = int(time.time()) + 60
```

## 部署前檢查清單

- 外部資料在進入 LLM context 之前先經過清理
- 花費上限獨立於模型輸出之外強制執行
- 交易在送出前先模擬
- `min_amount_out` 是必填
- Circuit breaker 在回撤或無效狀態時停止
- 金鑰來自環境變數或 secret manager，絕對不放在程式碼或 log 裡
- 適當時使用私有 mempool 或受保護的路由
- 依策略設定 slippage 與期限
- 所有 agent 決策都要寫入 audit log，不只是成功送出的那些
