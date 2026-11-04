---
name: codebase-design
description: 設計深模組（deep module）的共用詞彙。當使用者想設計或改進 module 的介面、找出可以加深的機會、決定 seam 該放哪、讓程式碼更好測試或更好讓 AI 導覽，或其他 skill 需要深模組詞彙時使用。
---

# Codebase 設計

設計**深模組**：小小的介面背後藏著大量行為，放在乾淨的 seam 上，透過那個介面就能測試。只要是在設計或重構程式碼，就用這套語言和原則。目標是讓呼叫端得到 leverage、讓維護者得到 locality、讓所有人都好測試。

## 詞彙表

這些詞要照原意使用：不要換成「component」「service」「API」或「boundary」。用語一致就是重點。

**Module**：任何有介面和實作的東西。刻意不限規模：可以是函式、class、package，或橫跨好幾層的切片。_避免用_：unit、component、service。

**Interface**：呼叫端為了正確使用這個 module 必須知道的一切：型別簽章，還有 invariant、順序限制、錯誤模式、必要設定和效能特性。_避免用_：API、signature（太窄，它們只指型別層級的表面）。

**Implementation**：module 裡面的東西，也就是它的程式碼本體。跟 **Adapter** 是兩回事：一個東西可以是實作很大的小 adapter（Postgres repo），也可以是實作很小的大 adapter（in-memory fake）。討論重點是 seam 的時候用「adapter」，其他時候用「implementation」。

**Depth**：介面上的 leverage。呼叫端（或測試）每多學一單位的介面，能操作到多少行為。當大量行為藏在小介面後面，module 就是**深**的；介面幾乎跟實作一樣複雜，就是**淺**的。

**Seam** _(Michael Feathers)_：一個不必在原地修改就能改變行為的地方；也就是 module 的介面所在的*位置*。seam 放哪是獨立的設計決策，跟它背後放什麼是兩回事。_避免用_：boundary（跟 DDD 的 bounded context 混在一起了）。

**Adapter**：在 seam 上滿足某個介面的具體東西。描述的是*角色*（它填哪個位子），不是本質（它裡面是什麼）。

**Leverage**：呼叫端從深度得到的東西。每多學一單位的介面，就得到更多能力。一份實作可以在 N 個呼叫點和 M 個測試上回本。

**Locality**：維護者從深度得到的東西。改動、bug、知識和驗證都集中在同一個地方，而不是散在各個呼叫端。修一次，到處都好。

## 深 vs 淺

**深模組** = 小介面 + 大量實作：

```
┌─────────────────────┐
│   Small Interface   │  ← 方法少、參數簡單
├─────────────────────┤
│                     │
│  Deep Implementation│  ← 複雜邏輯藏起來
│                     │
└─────────────────────┘
```

**淺模組** = 大介面 + 很少實作（要避免）：

```
┌─────────────────────────────────┐
│       Large Interface           │  ← 方法多、參數複雜
├─────────────────────────────────┤
│  Thin Implementation            │  ← 只是轉手而已
└─────────────────────────────────┘
```

設計介面時，問自己：

- 方法數量能不能減少？
- 參數能不能簡化？
- 能不能把更多複雜度藏進裡面？

## 原則

- **深度是介面的性質，不是實作的性質。** 深模組內部可以由小的、可 mock 的、可替換的零件組成；它們只是不屬於介面。module 可以有**內部 seam**（實作私有的，給自己的測試用），也有位於介面的**外部 seam**。
- **刪除測試。** 想像把這個 module 刪掉。如果複雜度跟著消失，它就只是個轉手的 pass-through。如果複雜度重新出現在 N 個呼叫端，代表它有在做事。
- **介面就是測試表面。** 呼叫端和測試跨過同一條 seam。如果你想測*介面之外*的東西，這個 module 的形狀多半不對。
- **一個 adapter 代表假設性的 seam，兩個 adapter 才是真的 seam。** 除非真的有東西會在這條 seam 兩邊變動，否則不要引入 seam。

## 為可測試性而設計

好的介面讓測試變得自然：

1. **接收依賴，不要自己建立。**

   ```typescript
   // 好測試
   function processOrder(order, paymentGateway) {}

   // 難測試
   function processOrder(order) {
     const gateway = new StripeGateway();
   }
   ```

2. **回傳結果，不要產生副作用。**

   ```typescript
   // 好測試
   function calculateDiscount(cart): Discount {}

   // 難測試
   function applyDiscount(cart): void {
     cart.total -= discount;
   }
   ```

3. **表面積要小。** 方法越少，需要的測試越少。參數越少，測試的準備越簡單。

## 關係

- 一個 **Module** 剛好有一個 **Interface**（它呈現給呼叫端和測試的表面）。
- **Depth** 是 **Module** 的性質，拿它的 **Interface** 來衡量。
- **Seam** 是 **Module** 的 **Interface** 所在的位置。
- **Adapter** 坐落在 **Seam** 上，並滿足 **Interface**。
- **Depth** 為呼叫端帶來 **Leverage**，為維護者帶來 **Locality**。

## 被否決的說法

- **把 depth 當成實作行數對介面行數的比值**（Ousterhout）：這會獎勵灌水實作。我們改用 depth-as-leverage。
- **把「Interface」當成 TypeScript 的 `interface` 關鍵字或 class 的 public method**：太窄：這裡的 interface 包含呼叫端必須知道的每一件事。
- **「Boundary」**：跟 DDD 的 bounded context 混在一起了。請說 **seam** 或 **interface**。

## 進一步深入

- **在已知依賴的情況下加深一整群 module**，見 [DEEPENING.md](DEEPENING.md)：依賴的分類、seam 的紀律，以及取代而不是疊層的測試方式。
- **探索替代的介面**，見 [DESIGN-IT-TWICE.md](DESIGN-IT-TWICE.md)：啟動平行的 sub-agent，用好幾種截然不同的方式設計介面，再從 depth、locality 和 seam 位置來比較。
