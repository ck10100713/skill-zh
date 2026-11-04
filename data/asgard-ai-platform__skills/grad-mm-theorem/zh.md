---
name: "grad-mm-theorem"
description: "用 Modigliani-Miller 定理分析資本結構決策，找出融資選擇何時會影響公司價值。當使用者需要評估負債與股權的取捨、評估槓桿對公司價值的影響、理解稅盾的好處，或問到「資本結構重要嗎」「我們該多借錢嗎」「最佳槓桿比率是多少」時，就用這個 skill。"
metadata:
  category: "WP-26 財務理論"
  tags: ["Modigliani-Miller", "capital-structure", "leverage", "tax-shield", "WACC", "tradeoff-theory"]
---

# Modigliani-Miller Theorem

## Overview

Modigliani-Miller 定理（1958）指出，在完美的資本市場中，公司價值和資本結構無關。這個無關性的結果是基準，現實世界中資本結構之所以重要的每個理由，都是在違反 MM 的假設。

## When to Use

- 評估某個融資決策是創造還是摧毀價值
- 找出哪些市場不完美，讓資本結構變得重要
- 計算負債稅盾的價值
- 教學或分析資本結構理論的邏輯基礎

## When NOT to Use

- 當成字面上的處方：現實的市場從來不是沒有摩擦的
- 分析需要明確建模破產成本（用抵換理論）
- 資本結構受到監管的金融機構

## Assumptions

```
IRON LAW: MM irrelevance holds ONLY in perfect markets — every
real-world deviation (taxes, bankruptcy costs, agency costs) makes
capital structure matter. MM is the null hypothesis, not the answer.
```

關鍵假設（針對無關性）：
1. 沒有稅（公司稅或個人稅）
2. 沒有破產成本或財務困境成本
3. 沒有代理成本，經理人依股東利益行事
4. 資訊對稱，內部人和外部人知道的一樣多
5. 個人和公司以相同利率借款

## Methodology

### Step 1 — State MM Propositions

- **命題 I（無稅）：** VL = VU，公司價值和槓桿無關
- **命題 II（無稅）：** Re = R0 + (D/E)(R0 - Rd)，股權成本隨槓桿線性上升
- **命題 I（有稅）：** VL = VU + Tc x D，負債創造稅盾

### Step 2 — Identify Market Imperfections

針對每個偏離，評估其大小：
- 公司稅：創造使用負債的誘因（稅盾）
- 破產成本：創造反對過度負債的誘因
- 代理成本：負債約束經理人（Jensen，1986），但可能造成資產替代
- 資訊不對稱：導致啄食順序（pecking order）行為

### Step 3 — Apply Tradeoff Framework

最佳資本結構，是在邊際稅盾利益，和邊際破產成本與代理成本之間取得平衡。

### Step 4 — Compute WACC Impact

WACC = (E/V)Re + (D/V)Rd(1-Tc)。最佳結構會讓 WACC 最小。

## Output Format

```markdown
## Capital Structure Analysis: [Firm]

### Current Structure
| Metric | Value |
|--------|-------|
| Debt (D) | $X |
| Equity (E) | $X |
| D/E Ratio | x.xx |
| WACC | x% |

### MM Imperfections Present
| Imperfection | Magnitude | Direction |
|-------------|-----------|-----------|
| Tax shield | [high/medium/low] | Favors debt |
| Bankruptcy costs | [high/medium/low] | Favors equity |
| Agency costs | [high/medium/low] | [depends] |

### Recommendation
- [Optimal direction of adjustment with reasoning]
```

## Gotchas

- MM 命題 II 常被誤解：WACC 維持不變（無稅），因為較便宜的負債，剛好被上升的股權成本抵消
- 稅盾價值 Tc x D 假設負債是永續的，暫時性的負債需要用現值計算
- 個人稅（Miller，1977）可能抵消負債在公司稅上的優勢
- 實證上的槓桿比率因產業而異，差距極大，顯示沒有單一的「最佳」結構
- 財務困境成本很難衡量，但可能占公司價值的 10% 到 20%
- MM 假設營運現金流和融資無關，當槓桿影響投資決策時，這個假設就不成立

## References

- Modigliani, F. & Miller, M. (1958). The cost of capital, corporation finance and the theory of investment. *American Economic Review*, 48(3), 261-297.
- Modigliani, F. & Miller, M. (1963). Corporate income taxes and the cost of capital: a correction. *American Economic Review*, 53(3), 433-443.
- Jensen, M. (1986). Agency costs of free cash flow. *American Economic Review*, 76(2), 323-329.
