---
name: azure-kusto-irql
description: "為 Kusto 資安調查組合 IRQL（Incident Response Query Language）查詢。把自然語言的獵捕問題轉成由 Get_*、Extract_*、Enrich_* function 組成的可組合 IRQL pipeline。WHEN: IRQL query, security hunt, threat hunting KQL, incident response query, compose hunting pipeline, failed logins, phishing investigation, lateral movement, process execution, file creation events."
license: MIT
metadata:
  author: Microsoft
  version: "1.2.1"
---

# IRQL：Incident Response Query Language

用 selector、extractor、enricher 這些積木組合出 IRQL function pipeline。IRQL 把原始的 KQL 資安 table 包在語意明確、可組合的 function 後面，讓分析師（和 LLM）不用背 schema、叢集位置或 join key，就能表達獵捕邏輯。

## 啟動條件

使用者有以下情況時用這個 skill：
- 明確提到 IRQL、`Get_*`、`Extract_*` 或 `Enrich_*` function
- 說「use IRQL」或「write an IRQL query」
- 要求用已知的 IRQL selector 組合可組合的獵捕 pipeline

一般的資安查詢（例如「find failed logins」）**不要**啟動，除非使用者明確要求 IRQL。這類請求轉給 `azure-kusto`。

**這不是自然語言轉 IRQL 的轉換器。** 這個 skill 組合 IRQL function pipeline，可以處理能直接對應到已知 selector 和簡單過濾條件的基本自然語言需求。一般的自然語言轉 KQL 或轉 IRQL，請用專門的查詢產生 skill（另外提供）。

## IRQL Function 前置檢查

產生 pipeline 之前，先確認目標資料庫有 IRQL：

```kql
.show functions
| where Name startswith "Get_" or Name startswith "Extract_" or Name startswith "Enrich_"
| project Name
```

如果找不到任何 IRQL function，告訴使用者目標資料庫沒有部署 IRQL，並建議改用 `azure-kusto` 寫原始 KQL 查詢。IRQL function 是前提條件，這個 skill 不負責部署基礎的 IRQL selector。

## IRQL 是什麼

IRQL 是**建立在 KQL 之上、以 function 為基礎的方言**。它提供：

1. **統一的 schema**：不同來源的資安 table 會投影成一致的欄位名稱，不管底層資料來源是什麼
2. **可組合性**：小 function 用 `| invoke` 串起來，從簡單的步驟組出複雜的獵捕
3. **可移植性**：同一條 IRQL pipeline 可以在不同叢集/資料庫上跑；只需要把 `Get_*` 基本元件重新指向

IRQL 不是獨立的語言。它就是你去 invoke 的 KQL function。任何合法的 KQL 都可以跟 IRQL function 一起用。

## 部署 IRQL

IRQL function 是儲存的 KQL function（`.create-or-alter function`）。目標資料庫必須已經部署好它們，這個 skill 才能產生 pipeline。

**公開的範例叢集**（function 已預先部署）：
- 叢集：`https://kc7001.eastus.kusto.windows.net`
- 資料庫：`ValdyTimes`、`JoJosHospital`

要把 IRQL 移植到新的叢集/資料庫，先建立 `Get_*` selector，把你的來源 table 投影成統一的 schema（欄位名稱見下面），再部署 extractor 和 enricher。只要輸入的 schema 對得上，extractor 和 enricher 不用改就能用。

## Function 目錄

### 1. Selector：`Get_*`

回傳來源 table 經過投影、schema 統一的視圖。預設用最精簡的形式；需要額外欄位時再用 `_All`。

| Function | 欄位 |
|---|---|
| `Get_Event_Authentication` | `EnvTime`, `Hostname`, `ClientIp`, `Username`, `Result` |
| `Get_Event_Authentication_All` | + `Description`, `UserAgent`, `PasswordHash` |
| `Get_Email` | `EnvTime`, `EmailSender`, `EmailRecipient`, `Subject`, `Url` |
| `Get_Email_All` | + `ReplyTo`, `Verdict` |
| `Get_Employees` | `Name`, `ClientIp`, `Email`, `Username`, `Hostname`, `Role` |
| `Get_Employees_All` | + `HireDate`, `UserAgent`, `Domain` |
| `Get_Event_FileCreation` | `EnvTime`, `Hostname`, `Filename`, `Path` |
| `Get_Event_FileCreation_All` | + `Username`, `Sha256`, `ProcessName` |
| `Get_Event_NetworkInbound` | `EnvTime`, `ClientIp`, `Url` |
| `Get_Event_NetworkInbound_All` | + `Method`, `UserAgent`, `StatusCode` |
| `Get_Event_NetworkOutbound` | `EnvTime`, `ClientIp`, `Url` |
| `Get_Event_NetworkOutbound_All` | + `Method`, `UserAgent` |
| `Get_Dns_All` | `EnvTime`, `Domain`, `ClientIp` |
| `Get_Event_Process` | `EnvTime`, `ProcessCommandLine`, `ProcessName`, `Hostname`, `Username` |
| `Get_Event_Process_All` | + `ParentProcessName`, `ParentProcessHash`, `ProcessHash` |
| `Get_SecurityAlerts_All` | `EnvTime`, `AlertType`, `Severity`, `Description`, `Indicators` |
| `Get_Network_Connection_All` | `EnvTime`, `SourceIp`, `SourcePort`, `DestinationIp`, `DestinationPort`, `Protocol`, `Bytes` |

### 2. Extractor：`Extract_*`

從既有欄位衍生出新欄位。在 selector 之後 invoke。

| Function | 輸入欄位 | 新增 |
|---|---|---|
| `Extract_Email_Sender_Domain(T)` | `EmailSender` | `Domain` |
| `Extract_Employee_Firstname(T)` | `Name` | `Firstname` |
| `Extract_Event_Network_Domain(T)` | `Url` | `DomainName` |

### 3. Enricher：`Enrich_*`

用 left join 從相關 table 補上上下文的輔助 function。

| Function | Key 欄位 | 補充的內容 |
|---|---|---|
| `Enrich_Event_Authentication_Username(T)` | `Username` | 該使用者的認證事件 |
| `Enrich_Ip_Employee(T)` | `ClientIp` | 由 IP 查出員工身分 |
| `Enrich_Username_Employee(T)` | `Username` | 由使用者名稱查出員工身分 |
| `Enrich_Ip_Domain(T)` | `ClientIp` | 解析到該 IP 的 DNS 網域 |
| `Enrich_Ip_Event_NetworkOutbound(T)` | `ClientIp` | 來自該 IP 的對外網路流量 |
| `Enrich_Ip_Network_Connection(T)` | `ClientIp` | 來自該 IP 的網路 flow |

### 4. 外部補充

| Function | 來源 | 需求 |
|---|---|---|
| `Enrich_Sha256_VirusTotal(T)` | VirusTotal 檔案報告 | API key + callout policy |
| `Get_CISA_KEV()` / `Enrich_CISA_KEV(T)` | CISA KEV 目錄 | Callout policy |

## 組合規則

```
Selector -> Extract -> Filter -> Enrich -> Summarize/Project
```

1. **從 Selector 開始**：`Get_Event_Authentication`、`Get_Email` 等
2. **Extract** 衍生欄位：`| invoke Extract_Email_Sender_Domain()`
3. **Filter** 出訊號：`| where Result == "Failed Login"`
4. **Enrich** 補上下文：`| invoke Enrich_Username_Employee()`
5. **Summarize / project** 出答案

步驟之間一定要用 pipe（`|`）。Extractor 和 Enricher 用 `| invoke FunctionName()`。

## 查詢產生準則

- 預設用**最精簡的 selector**，需要額外欄位才用 `_All`
- extractor 放在 enricher 之前（extractor 新增的欄位，enricher 可能拿來當 key）
- `where` 過濾條件盡量放前面
- 聚合用 `summarize`，最後選欄位用 `project`
- 最後用 `order by` + `take` 限制輸出

## 範例

更多 prompt 和實作範例見 [references/EXAMPLES.md](references/EXAMPLES.md)。

### 暴力破解偵測
```kql
Get_Event_Authentication
| where Result == "Failed Login"
| summarize FailedCount = count() by Username
| where FailedCount > 19
| invoke Enrich_Username_Employee()
| project Username, Name, Role, Email, FailedCount
| order by FailedCount desc
```

### 依收件人職級做釣魚信件分級
```kql
Get_Email
| invoke Extract_Email_Sender_Domain()
| project EnvTime, EmailSender, Domain, Username = EmailRecipient, Subject, Url
| invoke Enrich_Username_Employee()
| extend Seniority = case(
    Role has_any ("CEO", "Chief", "Director", "VP", "President"), 3,
    Role has_any ("Manager", "Lead", "Senior"), 2,
    1)
| summarize
    TotalEmails = count(),
    SeniorityScore = sum(Seniority),
    Recipients = make_set(Name, 50),
    DistinctRecipients = dcount(Username)
  by Domain
| where DistinctRecipients >= 2
| order by SeniorityScore desc
| take 20
```

### 從入侵指標出發的後續滲透樞紐分析
```kql
let victims =
    Get_Event_FileCreation_All
    | where Filename has "<INDICATOR>"
    | distinct Hostname;
Get_Event_Process
| where Hostname in (victims)
| where ProcessCommandLine has_any ("rundll32", "regsvr32", "powershell", "systeminfo")
| project EnvTime, Hostname, Username, ProcessName, ProcessCommandLine
| order by EnvTime asc
```

### 補上身分資訊的可疑對外流量
```kql
Get_Event_NetworkOutbound
| invoke Extract_Event_Network_Domain()
| where DomainName has_any ("<SUSPICIOUS_DOMAIN_1>", "<SUSPICIOUS_DOMAIN_2>")
| invoke Enrich_Ip_Employee()
| project EnvTime, Name, Role, DomainName, Url, ClientIp
| order by EnvTime desc
```

### 外部 IP 認證異常
```kql
Get_Event_Authentication_All
| where not(ClientIp startswith "10.") and not(ClientIp startswith "192.168.")
| summarize
    Attempts = count(),
    Failures = countif(Result == "Failed Login"),
    Users = make_set(Username)
  by ClientIp
| order by Failures desc
| take 20
```

## 使用的 MCP 工具

| 工具 | 用途 |
|------|---------|
| `kusto_query` | 對 Kusto 資料庫執行 IRQL pipeline |
| `kusto_table_schema_get` | 找出有哪些 table 和欄位可用 |
| `kusto_cluster_list` | 列出可用的 ADX 叢集 |
| `kusto_database_list` | 列出叢集裡的資料庫 |

## 在 Kusto Explorer 裡開啟查詢（僅限 Windows）

> **選用的便利功能。** 預設流程是在對話裡輸出 KQL，讓使用者自己複製到 Kusto Explorer 或 VS Code 的 Kusto 擴充套件。自動啟動只在使用者選擇啟用時才做。

一律在對話回覆裡輸出完整的 KQL 查詢，並清楚標示 Step 1（連線）和 Step 2（查詢）：

```
// Step 1: Connect to your cluster (skip if already connected)
// Example: uncomment to connect to the KC7 training cluster
// #connect cluster('kc7001.eastus.kusto.windows.net').database('ValdyTimes')
// Or replace with your own cluster:
// #connect cluster('<YOUR_CLUSTER>').database('<YOUR_DATABASE>')

// Step 2: Run the query below
<KQL_QUERY>
```

如果使用者要求存檔或在 Kusto Explorer 裡開啟，照 [references/KUSTO_EXPLORER_LAUNCH.md](references/KUSTO_EXPLORER_LAUNCH.md) 的流程做。重點規則：

- 寫檔或啟動執行檔之前，用 `ask_user` 確認
- 把檔案內容顯示在對話裡，讓使用者開啟前能先檢查
- 絕對不准用 shell 插值或 here-string，檔案要用 `Set-Content`/`Add-Content` 寫
- 絕對不准把查詢編碼進瀏覽器 URL
- 在 macOS/Linux 上，存成 `.kql` 檔，然後建議用 VS Code 的 Kusto 擴充套件或 ADX Web Explorer
- 要用 IRQL 資料做 graph 視覺化，看 `azure-kusto-graph` 和 `azure-kusto-irql-graph`
