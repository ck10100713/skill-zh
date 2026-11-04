---
name: error-handling-patterns
description: 精通跨語言的錯誤處理模式，包含 exception、Result 型別、錯誤傳遞與優雅降級，用來建構有韌性的應用。適用於實作錯誤處理、設計 API，或提升應用可靠度的時候。
---

# 錯誤處理模式

用穩健的錯誤處理策略打造有韌性的應用，優雅地處理失敗並提供絕佳的除錯體驗。

## 什麼時候用這個 Skill

- 在新功能中實作錯誤處理
- 設計能容錯的 API
- 除錯 production 問題
- 提升應用程式的可靠度
- 為使用者與開發者寫出更好的錯誤訊息
- 實作 retry 與 circuit breaker 模式
- 處理非同步/並行的錯誤
- 建構容錯的分散式系統

## 核心概念

### 1. 錯誤處理的哲學

**Exception vs Result 型別：**

- **Exception**：傳統的 try-catch，會打斷控制流程
- **Result 型別**：明確表示成功/失敗，函數式的做法
- **錯誤碼**：C 風格，需要紀律
- **Option/Maybe 型別**：用於可為 null 的值

**什麼時候用哪個：**

- Exception：非預期的錯誤、例外狀況
- Result 型別：預期內的錯誤、驗證失敗
- Panic/Crash：無法復原的錯誤、程式 bug

### 2. 錯誤分類

**可復原的錯誤：**

- 網路 timeout
- 檔案不存在
- 無效的使用者輸入
- API 速率限制

**無法復原的錯誤：**

- 記憶體不足
- Stack overflow
- 程式 bug（null pointer 等）

## 詳細模式與實作範例

詳細的模式文件放在 `references/details.md`，上面這一層導覽不夠用的時候再去讀那份檔案。

## 最佳實務

1. **快速失敗**：及早驗證輸入，快速失敗
2. **保留 context**：包含 stack trace、metadata、時間戳
3. **有意義的訊息**：說明發生了什麼事，以及怎麼修
4. **適度記 log**：錯誤就記 log，預期內的失敗不要洗版
5. **在對的層級處理**：在你能有意義地處理的地方才 catch
6. **清理資源**：使用 try-finally、context manager、defer
7. **不要吞掉錯誤**：要記 log 或重新丟出，不要默默忽略
8. **型別安全的錯誤**：可以的話用具型別的錯誤

```python
# 良好的錯誤處理範例
def process_order(order_id: str) -> Order:
    """以完整的錯誤處理來處理訂單。"""
    try:
        # 驗證輸入
        if not order_id:
            raise ValidationError("Order ID is required")

        # 取得訂單
        order = db.get_order(order_id)
        if not order:
            raise NotFoundError("Order", order_id)

        # 處理付款
        try:
            payment_result = payment_service.charge(order.total)
        except PaymentServiceError as e:
            # 記 log 並包裝外部服務的錯誤
            logger.error(f"Payment failed for order {order_id}: {e}")
            raise ExternalServiceError(
                f"Payment processing failed",
                service="payment_service",
                details={"order_id": order_id, "amount": order.total}
            ) from e

        # 更新訂單
        order.status = "completed"
        order.payment_id = payment_result.id
        db.save(order)

        return order

    except ApplicationError:
        # 重新丟出已知的應用程式錯誤
        raise
    except Exception as e:
        # 記錄非預期的錯誤
        logger.exception(f"Unexpected error processing order {order_id}")
        raise ApplicationError(
            "Order processing failed",
            code="INTERNAL_ERROR"
        ) from e
```

## 常見陷阱

- **捕捉範圍太廣**：`except Exception` 會藏住 bug
- **空的 catch 區塊**：默默吞掉錯誤
- **記 log 又重新丟出**：會產生重複的 log
- **沒有清理**：忘記關閉檔案、連線
- **糟糕的錯誤訊息**：「發生錯誤」一點用也沒有
- **回傳錯誤碼**：改用 exception 或 Result 型別
- **忽略非同步錯誤**：未處理的 promise rejection
