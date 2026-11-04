---
name: mailtrap-email-integration
description: 引導 agent 透過 Mailtrap 的 Email API 整合交易型 email 寄送，包含 sandbox 測試、網域驗證與 API 驗證。在實作寄信功能、除錯寄送問題，或設定安全的 dev/staging email 測試時使用。
origin: ECC
---

# Mailtrap Email 整合

使用 Mailtrap 的 Email API 與 Sandbox，為應用程式加入交易型 email 寄送的模式，涵蓋驗證、環境隔離與常見的寄送陷阱。

## 何時啟用

- 實作「寄 email」功能（註冊確認、重設密碼、通知、收據）
- 除錯為什麼 email 沒有寄到 dev/staging
- 為專案設定第一個寄 email 的整合
- Review 直接呼叫 email API 而沒有 sandbox 隔離的程式碼

## 核心概念

**Sandbox 與 Production 隔離。**Mailtrap 提供 Sandbox API，只攔截 email 而不實際投遞，用於 dev/staging，讓測試 email 永遠不會寄到真實的收件匣。Production 寄送使用另一個已驗證網域的 endpoint。絕對不要讓 dev 環境指向 production 的寄送 endpoint。

**驗證。**請求在 `Authorization` header 中使用 Bearer token。Token 以專案為範圍；sandbox 與 production 通常使用不同的 token。

**網域驗證。**Production 寄送需要先透過 DNS 紀錄（SPF、DKIM、DMARC）驗證寄件網域，Mailtrap 才會投遞給真實的收件人。跳過這步會造成無聲的寄送失敗，或被放進垃圾郵件匣。

## 程式碼範例

```typescript
// Sending via Mailtrap's Email API (production)
async function sendEmail(to: string, subject: string, html: string) {
  const response = await fetch("https://send.api.mailtrap.io/api/send", {
    method: "POST",
    headers: {
      "Authorization": `Bearer ${process.env.MAILTRAP_API_TOKEN}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      from: { email: "no-reply@yourverifieddomain.com", name: "Your App" },
      to: [{ email: to }],
      subject,
      html,
    }),
  });

  if (!response.ok) {
    throw new Error(`Email send failed: ${response.status}`);
  }
  return response.json();
}
```

```typescript
// Same call, routed to Sandbox in non-production environments
const MAILTRAP_ENDPOINT = process.env.NODE_ENV === "production"
  ? "https://send.api.mailtrap.io/api/send"
  : `https://sandbox.api.mailtrap.io/api/send/${process.env.MAILTRAP_INBOX_ID}`;
```

## 反模式

| 反模式 | 為什麼是問題 | 改成 |
| --- | --- | --- |
| 在 dev/test 使用 production 的寄送 endpoint | 真實的測試 email 會寄到真實的收件匣，有被檢舉垃圾郵件與測試資料外洩的風險 | 把非 production 環境導向 Sandbox endpoint |
| 把 API token 寫死在原始碼裡 | 一旦 commit 進版本控制就有憑證外洩的風險 | 從環境變數 / secret manager 載入 token |
| 網域驗證還沒完成就寄信 | email 無聲失敗或落入垃圾郵件 | 啟用 production 寄送之前，先驗證 SPF/DKIM/DMARC 紀錄 |
| 寄送失敗時沒有 retry/錯誤處理 | 通知無聲失敗（例如使用者一直收不到重設密碼的 email） | 檢查 response status、記錄失敗、顯示可操作的錯誤 |

## 最佳實務

- sandbox 與 production 的 token 放在不同的環境變數，絕對不要一個 token 跨環境共用
- 任何涉及 email 的 production 上線之前，先驗證寄件網域的 DNS 紀錄
- 記錄寄送失敗時，附上足夠除錯的 context（收件人、範本、時間戳、response code）
- 把寄 email 當成可能失敗的網路呼叫：用 try/catch 包起來，絕對不要假設成功

## 相關 Skill

`api-and-interface-design`, `security-and-hardening`, `ci-cd-and-automation`
