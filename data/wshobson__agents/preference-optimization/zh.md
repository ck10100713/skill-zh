---
name: preference-optimization
description: 用 DPO、ORPO、KTO 或 SimPO，以偏好資料讓微調後的模型對齊。在有偏好配對或讚/倒讚回饋、要在偏好最佳化方法之間做選擇，或 DPO 訓練需要超參數或除錯時使用。
---

# Preference Optimization

這個 skill 假設 `finetuning-method-selection`
已經把你導到這裡，因為資料的形態是
偏好配對，或沒有配對的讚/倒讚
回饋，不是示範資料（那是
`lora-qlora-recipes`），也不是可驗證的 reward
訊號（那是 `grpo-rlvr-training`）。
接下來講的是 DPO 家族內的方法選擇、
這個選擇實際上有多重要的證據、
正式環境的訓練模式，以及
一開始要怎麼建立這些配對。

**輸入：** 一個路由決策（偏好
最佳化）加上偏好配對或沒有配對的
回饋，通常來自某個 SFT checkpoint。
**輸出格式：** 一個驗證過的方法選擇加上
一份設定，也就是
`references/method-configs.md` 裡的 kwarg 值，不是自由發揮的
建議，`llm-finetuning-training-engineer`
會直接使用它。

## Method Selection

| Data shape | Method | Key parameters |
|---|---|---|
| Preference pairs, default case | **DPO** | β=0.1, LR 5e-7–1e-6, 1–2 epochs |
| Memory-bound or no SFT checkpoint | **ORPO** | reference-free, fused SFT+preference in one loss |
| Unpaired thumbs-up/down | **KTO** | binary label per example, no pairing needed |
| Length bias observed, sweep budget available | **SimPO** | reference-free; see sweep grid below |

- **DPO 是安全的預設選擇。** 使用 β=0.1，
  learning rate 5e-7 到 1e-6，跑 1 到 2 個 epoch。
  這個 LR *低於*產出這個待對齊 checkpoint 的
  SFT LR，把 SFT 規模的 LR 搬到 DPO 訓練裡，
  是這裡最常見的設定錯誤，不是邊角案例。
- **ORPO** 適用在記憶體是
  限制，或是沒有獨立的 SFT
  checkpoint 可以起手的時候，它不需要 reference，
  而且把 SFT 與偏好目標融合成
  一個 loss，省掉獨立的 SFT 階段，
  也省掉 DPO 要背的
  reference model 記憶體成本。
- **KTO** 適用在回饋是沒有配對的
  二元訊號（讚/倒讚），而不是
  成對的偏好配對的時候，不要為了改用 DPO，
  硬把沒有配對的回饋拼成合成配對。
- **SimPO** 修正了 DPO 的長度偏差，但只有
  在有紀律地掃參數時才划算，它發表的
  成果是在調過的掃參下報告的上限，
  不是任何單一設定都能重現的 baseline。
  只有在有掃參預算時才導向這裡；沒有的話就用
  DPO。
- **傳統 RLHF（reward model + PPO）已經淘汰**，
  除了前沿實驗室之外。不要在正式環境的
  pipeline 裡去用它，對於同樣的資料形態，
  上面的每個方法都更便宜、也有更好的支援。

### Worked Examples

- *「我們有一個 SFT checkpoint 和乾淨的成對
  偏好資料，目前還沒有長度偏差的抱怨。」*
  → 預設情況 → β=0.1 的 **DPO**。
- *「審查者對每個回應按讚/倒讚；
  沒有任何東西是配對的。」* → 沒有配對的訊號 →
  **KTO**，不是 DPO，不要為了把
  DPO 套到沒有配對的資料上而合成配對。
- *「GPU 預算不夠同時跑獨立的 SFT 階段
  加一個 DPO reference model。」* → 受記憶體限制，
  沒有獨立的 checkpoint → **ORPO**。
- *「DPO 的輸出不管品質好壞都偏好比較長的答案，
  而且有時間跑一次掃參。」* →
  長度偏差加上有掃參預算 → **SimPO**。如果
  其實沒有掃參預算就跳過它。

## The Low-Leverage Truth

一份 2026 年、跑了 240 次 H100 的研究（arXiv 2603.19335）
是上面那張表背後承重的證據：
**loss function 的選擇大約只有 1
個百分點的槓桿，模型規模
大約有 50 個百分點。** 測試的 20 個 DPO 變體
沒有任何一個勝過原版 DPO。排名也會**隨
規模反轉**，在小規模試驗中勝出的變體，
在部署規模時可能會輸。

兩個實際的結論：

- 不要花路由決策的力氣去煩惱
  DPO 變體的比較。上面那張表
  就夠了；跟資料品質與規模相比，更深入的變體選擇
  槓桿很低。
- **在相信排名之前，要先在部署規模上驗證。**
  在小型試驗模型上跑的方法比較，
  不會轉移到正式環境的
  規模等級，規模一變，就要重新檢查勝出的方法。

這也是上面的 Method Selection 表格
刻意寫得這麼短的原因：它編碼的是約 1 個百分點的槓桿，
不是 DPO 變體的排名，
同一份研究顯示那種排名跨規模並不成立。
任何不在那張表裡的變體選擇建議，
包括宣稱某個特定變體
「獲勝」的建議，在目標部署規模上驗證過之前，
都視為未經證實。

## Production Pattern: Iterative On-Policy DPO

在靜態偏好資料集上跑單次 offline DPO，
只是個起點，不是正式環境的模式。
隨著訓練進行，policy 會偏離
這些配對取樣時的分布，
靜態資料集會因為這種偏離而過期。
正式環境的 pipeline 改成迭代地、on-policy 地
跑 DPO：

1. 從目前的 policy checkpoint 取樣
   completion。
2. 對 completion 評分或排序（reward model、
   judge 或任務評分器）。
3. 用目前的 checkpoint 當作 reference model，
   跑一輪 DPO。
4. 產出的 checkpoint 同時成為新的
   policy *和*下一輪的新 reference。

重複這個流程。每一輪的 reference model 是上一輪
的輸出，不是固定的初始 checkpoint，
這樣才能讓偏好訊號維持 on-policy，
不是拿越來越過期的分布來評分。

單次 DPO 仍然是合理的第一次迭代，
只是它不是整個 pipeline。
第一個 checkpoint 出來之後，至少要規劃再跑一輪，
不要把第一輪當成最終成品。

## Pair Construction

用**同一個任務中通過與失敗的軌跡**來建立 DPO/ORPO 配對，
也就是對同一個底層任務的兩次嘗試，
不是從不同任務裡挑出來、互不相關的
最好與最差的範例。在那個軌跡集合內，
要在 **reward 分布的 μ−2σ 處選出 rejected 的那一筆，
絕對不要選最小值**。天真的
最好對最差的配對建構（最大 reward 對
絕對最小值）會隨規模增加而變差；
μ−2σ 的選法，對上面低槓桿研究
揭露的同一種規模敏感性，會更穩健。

```
sorted_by_reward = sort(trajectories, key=reward)
chosen   = sorted_by_reward[-1]                # highest reward
mu, sigma = mean(rewards), stdev(rewards)
rejected = closest(sorted_by_reward, mu - 2 * sigma)
# NOT sorted_by_reward[0] — the absolute minimum
# is the naive best-vs-worst construction that
# degrades as scale increases.
```

關於怎麼把評分過的 trace 變成
這些配對的做法，包括 rejection sampling 和
由 judge 評分的差距選取，請見
`trace-to-training-data`。

## References

每個方法完整的 TRL 設定區塊，
也就是 `DPOConfig`、`ORPOConfig`、`KTOConfig`，以及
SimPO 的掃參網格，加上 Unsloth 的包裝和一則
災難性遺忘的備註，放在
`references/method-configs.md`。那些設定使用
`lora-qlora-recipes` 的
`references/unsloth-trl-mapping.md` 裡
建立的同一套目前 TRL API 慣例
（用 `processing_class`，不是 `tokenizer=`）。

`references/method-configs.md` 也帶有
災難性遺忘的備註：當偏好調校過的
checkpoint 失去通用能力時，learning rate 過高
通常就是原因，修正方式
幾乎總是先把 LR 降到上面 Method Selection 表格中
範圍的低端，再去考慮其他補救方法。

相關 skill：一旦有了偏好配對或沒有配對的
回饋，`finetuning-method-selection`
會導向這裡；`lora-qlora-recipes` 產出
DPO/KTO/SimPO 要對齊的 SFT checkpoint
（ORPO 的融合路徑可以跳過它）；`trace-to-training-data`
把通過/失敗的軌跡轉換成
這個 skill 的 Pair Construction 段落
所使用的配對。
