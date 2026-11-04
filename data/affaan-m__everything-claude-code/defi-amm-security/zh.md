---
name: defi-amm-security
description: Solidity AMM 合約、流動性池和 swap 流程的安全檢查清單。涵蓋 reentrancy、CEI 順序、donation 或 inflation 攻擊、oracle 操弄、slippage、管理員控制，以及整數運算。在審計或撰寫 Solidity AMM、流動性池或 swap 程式碼時使用。
metadata:
  version: "1.0.0"
  origin: ECC direct-port adaptation
---

# DeFi AMM 安全

給 Solidity AMM 合約、LP vault 和 swap 函式用的關鍵漏洞模式與加固後的實作。

## 何時使用

- 撰寫或審計 Solidity 的 AMM 或流動性池合約
- 實作會持有 token 餘額的 swap、deposit、withdraw、mint 或 burn 流程
- 審查任何在份額或準備金運算裡用到 `token.balanceOf(address(this))` 的合約
- 對 DeFi 協議加上手續費設定函式、暫停功能、oracle 更新或其他管理員函式

## 運作方式

把它當成「檢查清單加模式庫」來用。針對下面各個類別，逐一審查每個使用者進入點，並且優先採用加固過的範例，不要自己手寫變體。

## 執行安全

這個 skill 裡的 shell 指令都是本機審計的範例。只能在可信任的 checkout 或用完即丟的沙箱裡執行，而且不要把不受信任的合約名稱、路徑、RPC URL、私鑰或使用者提供的 flag 拼進 shell 指令裡。安裝工具，或執行可能耗用大量本機或付費資源的長時間 fuzzing/靜態分析作業之前，要先問過。

絕對不要把 secret、私鑰、助記詞、API token 或主網簽署憑證放進指令範例、log 或報告裡。

## 範例

### Reentrancy：落實 CEI 順序

有漏洞的寫法：

```solidity
function withdraw(uint256 amount) external {
    require(balances[msg.sender] >= amount);
    token.transfer(msg.sender, amount);
    balances[msg.sender] -= amount;
}
```

安全的寫法：

```solidity
import {ReentrancyGuard} from "@openzeppelin/contracts/utils/ReentrancyGuard.sol";
import {SafeERC20} from "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";

using SafeERC20 for IERC20;

function withdraw(uint256 amount) external nonReentrant {
    require(balances[msg.sender] >= amount, "Insufficient");
    balances[msg.sender] -= amount;
    token.safeTransfer(msg.sender, amount);
}
```

已經有加固過的函式庫時，不要自己寫 guard。

### Donation 或 inflation 攻擊

直接用 `token.balanceOf(address(this))` 做份額運算，會讓攻擊者透過非預期的路徑把 token 送進合約，藉此操弄分母。

```solidity
// Vulnerable
function deposit(uint256 assets) external returns (uint256 shares) {
    shares = (assets * totalShares) / token.balanceOf(address(this));
}
```

```solidity
// Safe
uint256 private _totalAssets;

function deposit(uint256 assets) external nonReentrant returns (uint256 shares) {
    uint256 balBefore = token.balanceOf(address(this));
    token.safeTransferFrom(msg.sender, address(this), assets);
    uint256 received = token.balanceOf(address(this)) - balBefore;

    shares = totalShares == 0 ? received : (received * totalShares) / _totalAssets;
    _totalAssets += received;
    totalShares += shares;
}
```

要自己追蹤內部帳務，並且量測實際收到的 token 數量。

### Oracle 操弄

現貨價格可以被閃電貸操弄。優先用 TWAP。

```solidity
uint32[] memory secondsAgos = new uint32[](2);
secondsAgos[0] = 1800;
secondsAgos[1] = 0;
(int56[] memory tickCumulatives,) = IUniswapV3Pool(pool).observe(secondsAgos);
int24 twapTick = int24(
    (tickCumulatives[1] - tickCumulatives[0]) / int56(uint56(30 minutes))
);
uint160 sqrtPriceX96 = TickMath.getSqrtRatioAtTick(twapTick);
```

### Slippage 保護

每條 swap 路徑都需要由呼叫者提供的 slippage 和 deadline。

```solidity
function swap(
    uint256 amountIn,
    uint256 amountOutMin,
    uint256 deadline
) external returns (uint256 amountOut) {
    require(block.timestamp <= deadline, "Expired");
    amountOut = _calculateOut(amountIn);
    require(amountOut >= amountOutMin, "Slippage exceeded");
    _executeSwap(amountIn, amountOut);
}
```

### 安全的準備金運算

```solidity
import {FullMath} from "@uniswap/v3-core/contracts/libraries/FullMath.sol";

uint256 result = FullMath.mulDiv(a, b, c);
```

大額的準備金運算，在有 overflow 風險時，要避免天真的 `a * b / c`。

### 管理員控制

```solidity
import {Ownable2Step} from "@openzeppelin/contracts/access/Ownable2Step.sol";

contract MyAMM is Ownable2Step {
    function setFee(uint256 fee) external onlyOwner { ... }
    function pause() external onlyOwner { ... }
}
```

所有權轉移優先用明確的接受（acceptance）機制，並且對每條特權路徑都加上閘門。

## 安全檢查清單

- 有 reentrancy 風險的進入點都用 `nonReentrant`
- 遵守 CEI 順序
- 份額運算不依賴原始的 `balanceOf(address(this))`
- ERC-20 的轉帳使用 `SafeERC20`
- 存款時量測實際收到的 token 數量
- oracle 讀取使用 TWAP 或其他抗操弄的來源
- swap 要求 `amountOutMin` 和 `deadline`
- 對 overflow 敏感的準備金運算，使用 `mulDiv` 這類安全的原語
- 管理員函式有存取控制
- 有緊急暫停功能，而且有測試過
- 上 production 之前跑過靜態分析和 fuzzing

## 審計工具

```bash
pip install slither-analyzer
slither . --exclude-dependencies

echidna-test . --contract YourAMM --config echidna.yaml

forge test --fuzz-runs 10000
```
