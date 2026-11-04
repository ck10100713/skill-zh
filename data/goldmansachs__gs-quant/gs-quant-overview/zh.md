---
name: gs-quant-overview
description: "撰寫 gs_quant 程式碼的指南：session、金融商品、投資組合、定價與風險、結果、資料集與回測。只要是使用 gs_quant 函式庫的程式任務都適用，包括定價很慢、timeout、gs_quant 錯誤訊息，以及價格跟其他工具不一樣或看起來是前一天的。"
---

# gs_quant 快速上手

在寫任何要做定價、計算風險或 resolve 金融商品的程式碼之前，先讀 `pricing.md`。

## 1. 用 `GsSession.use` 建立 Session

`gs_quant` 所有的 API 通訊都經過一個已認證的 `GsSession`。在做任何定價或資料呼叫之前，一定要先用 `GsSession.use()` 初始化 session。

### OAuth2（應用程式憑證）

```python
from gs_quant.session import GsSession, Environment

GsSession.use(
    environment_or_domain=Environment.PROD,
    client_id='my_client_id',
    client_secret='my_client_secret',
    scopes=('run_analytics',),
)
```

- **`environment_or_domain`**：`Environment.PROD`（預設）、`Environment.QA` 或 `Environment.DEV`。也可以直接傳 URL 字串。
- **`client_id` / `client_secret`**：OAuth2 應用程式憑證。兩個都提供時，函式庫會建立 `OAuth2Session`。
- **`scopes`**：選填，一組 `GsSession.Scopes` 的值。通常替交易定價時會需要 `run_analytics`。

### 當成 Context Manager 使用

```python
with GsSession.get(Environment.PROD, client_id='...', client_secret='...') as session:
    # session is active inside this block
    ...
```

### 確認 Session

```python
GsSession.current  # the currently active GsSession instance
```

---

## 2. Resolve 一個金融商品

建立金融商品時，通常只會指定其中一部分參數。**Resolve** 會把商品送到 GS 的定價服務，補齊其餘所有欄位。

```python
from gs_quant.instrument import IRSwap

swap = IRSwap('Pay', '10y', 'USD')

# Before resolve: swap.fixed_rate is None
swap.resolve()
# After resolve: swap.fixed_rate is now populated with the current par rate

print(swap.fixed_rate)  # e.g. 0.0345
```

### `resolve()` 做了什麼

1. 把商品連同目前的 `PricingContext` 一起送到 GS 的分析服務。
2. 服務計算所有缺少的參數，像是 par rate、premium、forward points 等。
3. 預設（`in_place=True`）會就地更新商品。傳 `in_place=False` 則會拿到一份新的、已 resolve 的複本。

要把已輸入的交易 mark to market、讀取 resolve 後的條款，見 `pricing.md` 的「Relative terms and resolve()」。

---

## 3. 用 Portfolio 組合多個金融商品

`Portfolio` 類別把多個商品打包成一個單位，一起定價、resolve 和分析。

### 建立 Portfolio

```python
from gs_quant.instrument import IRSwap, IRSwaption
from gs_quant.markets.portfolio import Portfolio

swap = IRSwap('Pay', '10y', 'USD', name='USD 10y Payer')
swaption = IRSwaption('Receive', '10y', 'EUR', expiration_date='1y', name='EUR 1y10y Receiver')

portfolio = Portfolio([swap, swaption], name='My Portfolio')
```

從 dictionary 建立（key 會變成商品名稱）：

```python
portfolio = Portfolio(
    {
        'USD 10y Payer': IRSwap('Pay', '10y', 'USD'),
        'EUR 5y Receiver': IRSwap('Receive', '5y', 'EUR'),
    }
)
```

### 巢狀 Portfolio

```python
usd_book = Portfolio([IRSwap('Pay', '5y', 'USD'), IRSwap('Receive', '10y', 'USD')], name='USD Book')
eur_book = Portfolio([IRSwap('Pay', '5y', 'EUR')], name='EUR Book')
master = Portfolio([usd_book, eur_book], name='Master Book')
```

### Portfolio 操作

```python
portfolio.append(IRSwap('Pay', '2y', 'GBP'))  # add instruments
first = portfolio[0]  # access by index
usd_swap = portfolio['USD 10y Payer']  # access by name
len(portfolio)  # top-level count
portfolio.all_instruments  # all instruments across nested portfolios
```

### Resolve 與定價

```python
from gs_quant.risk import DollarPrice, IRDelta

portfolio.resolve()  # resolves all instruments in place
prices = portfolio.calc(DollarPrice)  # single risk measure
results = portfolio.calc([DollarPrice, IRDelta])  # multiple risk measures
```

---

## 延伸閱讀

要看特定主題的詳細說明，打開主題或症狀跟你手上任務對得上的那個檔案。

- `instruments.md`：建立所有類型的金融商品（IRSwap、XCcy swaps、FXOption、EqOption 等）、各資產類別的 strike，以及 FX 的常見陷阱
- `pricing.md`：PricingContext、HistoricalPricingContext 和 LiveMarket：用哪個收盤價、市場資料的位置、選擇 context、長時間計算與 `is_batch`、用 `use_cache` 快取結果、用 `Tracer` 追蹤慢或失敗的程式碼、relative terms 與 `resolve()`。症狀：程式很慢、請求很多、timeout、價格跟其他工具不一樣或看起來是前一天的。
- `scenarios.md`：對市場資料做衝擊與覆寫：各種寫法、衝擊幅度、股票 vol、FX 相關性、隨時間變化的衝擊損益。
- `risk-measures.md`：每個風險指標的數字代表什麼：單位、隨部位大小怎麼縮放、`currency=` 與 `aggregation_level=`，依資產類別區分。
- `errors.md`：gs_quant 的錯誤訊息和處理方式，以及都沒用時怎麼聯絡支援。
- `datasets.md`：透過 gs_quant 的 Dataset 類別取得市場與參考資料：get_data、get_data_series、get_data_last、get_coverage、上傳資料、大型查詢分批。涵蓋股票的 TREOD、FXIVOL_STANDARD、欄位與 symbol 維度查詢、指數成分股、已實現波動率、盤中資料，以及常見陷阱。
- `backtesting.md`：gs_quant 回測框架指南：什麼時候該直接定價就好、Strategy、trigger、action、GenericEngine、EquityVolEngine、交易成本、跳過日期、損益拆解和結果擷取。
- `measure.md`：用 `@plot_measure` 和 `@risk_measure` decorator 寫自訂指標
