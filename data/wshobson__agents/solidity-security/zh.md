---
name: solidity-security
description: 精通智能合約的安全最佳實務，預防常見漏洞並實作安全的 Solidity 模式。在撰寫智能合約、稽核既有合約，或為區塊鏈應用實作安全措施時使用。
---

# Solidity Security

精通智能合約的安全最佳實務、漏洞預防，以及安全的 Solidity 開發模式。

## When to Use This Skill

- 撰寫安全的智能合約
- 稽核既有合約的漏洞
- 實作安全的 DeFi 協議
- 預防 reentrancy、overflow 和存取控制問題
- 在維持安全的前提下優化 gas 用量
- 為專業稽核準備合約
- 了解常見的攻擊向量

## Detailed patterns and worked examples

詳細的 pattern 文件放在 `references/details.md`。上面這層導覽不夠用的時候，再去讀那個檔案。

## Testing for Security

```javascript
// Hardhat test example
const { expect } = require("chai");
const { ethers } = require("hardhat");

describe("Security Tests", function () {
  it("Should prevent reentrancy attack", async function () {
    const [attacker] = await ethers.getSigners();

    const VictimBank = await ethers.getContractFactory("SecureBank");
    const bank = await VictimBank.deploy();

    const Attacker = await ethers.getContractFactory("ReentrancyAttacker");
    const attackerContract = await Attacker.deploy(bank.address);

    // Deposit funds
    await bank.deposit({ value: ethers.utils.parseEther("10") });

    // Attempt reentrancy attack
    await expect(
      attackerContract.attack({ value: ethers.utils.parseEther("1") }),
    ).to.be.revertedWith("ReentrancyGuard: reentrant call");
  });

  it("Should prevent integer overflow", async function () {
    const Token = await ethers.getContractFactory("SecureToken");
    const token = await Token.deploy();

    // Attempt overflow
    await expect(token.transfer(attacker.address, ethers.constants.MaxUint256))
      .to.be.reverted;
  });

  it("Should enforce access control", async function () {
    const [owner, attacker] = await ethers.getSigners();

    const Contract = await ethers.getContractFactory("SecureContract");
    const contract = await Contract.deploy();

    // Attempt unauthorized withdrawal
    await expect(contract.connect(attacker).withdraw(100)).to.be.revertedWith(
      "Ownable: caller is not the owner",
    );
  });
});
```

## Audit Preparation

```solidity
contract WellDocumentedContract {
    /**
     * @title Well Documented Contract
     * @dev Example of proper documentation for audits
     * @notice This contract handles user deposits and withdrawals
     */

    /// @notice Mapping of user balances
    mapping(address => uint256) public balances;

    /**
     * @dev Deposits ETH into the contract
     * @notice Anyone can deposit funds
     */
    function deposit() public payable {
        require(msg.value > 0, "Must send ETH");
        balances[msg.sender] += msg.value;
    }

    /**
     * @dev Withdraws user's balance
     * @notice Follows CEI pattern to prevent reentrancy
     * @param amount Amount to withdraw in wei
     */
    function withdraw(uint256 amount) public {
        // CHECKS
        require(amount <= balances[msg.sender], "Insufficient balance");

        // EFFECTS
        balances[msg.sender] -= amount;

        // INTERACTIONS
        (bool success, ) = msg.sender.call{value: amount}("");
        require(success, "Transfer failed");
    }
}
```
