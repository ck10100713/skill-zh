---
name: azure-kusto-irql-graph
description: "把 IRQL graph function 套用到 KQL 或 IRQL 的查詢結果上，用於 Kusto Explorer 視覺化。產生 Lift_To_Graph 對應，並組合 Graph_Render_View、Graph_Fold_By_Property、Extract_Node_*、Enrich_Node_* 和 Enrich_Graph_* 的呼叫。接受使用者提供的查詢，或有限度的基本自然語言來源需求；它不是通用的自然語言轉 KQL/IRQL skill。WHEN: Lift_To_Graph, Graph_Render_View, Graph_Fold_By_Property, IRQL graph enrichment, graph mapping for existing query results, icon-decorated graph, fold graph nodes. 要做原生 make-graph 分析、graph-match、最短路徑、連通元件或持久化 graph，請用 azure-kusto-graph。"
license: MIT
metadata:
  author: Microsoft
  version: "1.2.1"
---

# IRQL Graph Function：從查詢結果到視覺化

把 IRQL graph function 家族套用到表格結果上。給定一個 KQL 或 IRQL 查詢，加上使用者對 graph 的描述，就產生 `Lift_To_Graph` 對應，並只組合需要的 stored graph function，在 Kusto Explorer 裡做視覺化、折疊、擷取或補充。來源查詢不一定要用 IRQL。

## 範圍與路由

| 需求 | 用哪個 |
|---|---|
| 把使用者提供的 KQL/IRQL 結果列轉成帶圖示的視覺化 graph | 這個 skill：`Lift_To_Graph` + `Graph_Render_View` |
| 折疊 node，或套用 `Extract_Node_*`、`Enrich_Node_*`、`Enrich_Graph_*` | 這個 skill |
| 用 `make-graph`、`graph-match`、最短路徑、連通元件、graph model 或 snapshot | `azure-kusto-graph` |
| 從自然語言寫出不簡單的 KQL/IRQL 調查查詢 | 先用 Kusto 或 IRQL 的查詢產生 skill，再用這個 skill |

如果需求同時有視覺化和原生 graph 分析，視覺化的 lift/render 部分用這個 skill，運算子語意用 `azure-kusto-graph`。除非使用者要求用原生 graph 運算子，否則不要把 graph-lift function 換成手工建的 edges 優先 graph。

## 輸入約定

- **偏好的輸入**：一個能跑、會產出表格結果的 KQL/IRQL 查詢，加上一段自然語言，描述想要的 node、edge、標籤、圖示、擷取、補充或折疊。
- 這個 skill **不是自然語言轉 KQL 或轉 IRQL 的轉換器**。它把既有的查詢結果轉成 graph 視覺化。一般的自然語言轉 KQL 或轉 IRQL，請用專門的查詢產生 skill（另外提供）。
- 保留使用者提供的查詢裡的取資料、join、過濾和聚合。只加 graph 對應需要的投影或合成 ID。
- 只有在能直接對應到單一已知 table 或 IRQL `Get_*` selector、欄位很明顯、過濾條件也簡單時，才支援基本的自然語言來源需求。要說明你假設的來源，不准自己編 join、schema 或調查邏輯。
- 不簡單的查詢建構，先用另一個 Kusto/IRQL 查詢產生 skill，再把這個 skill 套到它的輸出上。
- 如果沒有查詢或輸出 schema，來源又不簡單，產生對應之前要先請使用者提供 KQL 查詢或它的結果欄位。

## 啟動條件

使用者有以下情況時用這個 skill：
- 提供 KQL/IRQL 結果，並要求 IRQL graph 視覺化或對應
- 提到 `Lift_To_Graph`、`Graph_Render_View` 或 `Graph_Fold_By_Property`
- 要在 Kusto Explorer 裡做帶圖示的 node/edge 對應
- 想依共同屬性折疊/收合 node
- 要求透過 `Extract_Node_*`、`Enrich_Node_*` 或 `Enrich_Graph_*` 做 graph 擷取或補充

只為了 `graph-match`、graph 路徑/元件、持久化 graph 或一般的 `make-graph` 建構，不要啟動這個 skill；這些屬於 `azure-kusto-graph`。

**這不是自然語言轉 KQL/IRQL 的轉換器。** 輸入通常應該是一個能跑的 KQL 或 IRQL 查詢，它的結果需要 graph 視覺化。基本的自然語言來源需求只適用於單一 table/selector 這種簡單情況。一般的自然語言轉 KQL 或轉 IRQL，請用專門的查詢產生 skill（另外提供）。

## 環境

- **叢集**：`https://kc7001.eastus.kusto.windows.net`
- **資料庫**：`ValdyTimes`、`JoJosHospital`（graph function 已預先部署）
- **渲染**：Kusto Explorer 桌面應用程式（make-graph 視覺化視窗）
- **工具**：`kusto_query`（透過 Azure MCP Server）

### Function 前置檢查

`Lift_To_Graph` 和 `Graph_Render_View` 是 stored function，不是 Kusto 內建運算子。對目標資料庫產生或執行 lift pipeline 之前，先檢查部署了什麼：

```kql
.show functions
| where Name in~ ("Lift_To_Graph", "Graph_Render_View", "Graph_Fold_By_Property")
| project Name
```

- `Lift_To_Graph` 和 `Graph_Render_View` 是必要的。
- 只有要求折疊時才需要 `Graph_Fold_By_Property`。
- 用任何 `Extract_Node_*`、`Enrich_Node_*` 或 `Enrich_Graph_*` function 之前都要先檢查；不可用的話就省略選用的補充，除非使用者要你部署它。
- 如果缺了必要的 function，而你有權限修改資料庫，**部署之前先請使用者確認**。然後用 [references/DEPLOY_IRQL_FUNCTIONS.md](references/DEPLOY_IRQL_FUNCTIONS.md) 裡的 `.create-or-alter function` 定義。執行相關的 `.create-or-alter` 區塊，再重跑前置檢查確認。
- 如果沒有修改權限，告訴使用者缺哪些 function，並指引他們看 `references/DEPLOY_IRQL_FUNCTIONS.md` 手動部署。

## IRQL Graph Function 家族

### `Lift_To_Graph(T, mappingJson)`

把任何表格形式的 KQL 結果轉成統一的 node + edge table。

**輸入**：任意 table `T` + 一個 JSON 對應字串。
**輸出**：`EntityType` 是 `"node"` 或 `"edge"` 的列，可直接給 `make-graph` 用。

### `Graph_Render_View(T)`

接收 `Lift_To_Graph` 的輸出，把 node/edge 拆開，呼叫 `make-graph` 開啟 Kusto Explorer 的 graph 視窗。

### `Graph_Fold_By_Property(T, NodeType, PropertyName)`

把某個型別、屬性值相同的 node 收合成單一 node。edge 會自動重新接線。

### Graph 擷取與補充 Function

這些是額外的 stored function，必須已經部署在目標資料庫上。它們**不**包含在 `references/DEPLOY_IRQL_FUNCTIONS.md` 裡。放進 pipeline 之前，先用 `.show functions` 確認可不可用。

| Function | 操作 | 關鍵屬性 |
|---|---|---|
| `Extract_Node_Email_Sender_Domain(T, displayName)` | 在 node 屬性裡加上 `Domain` | `EmailSender` |
| `Extract_Node_Employee_Firstname(T, displayName)` | 在 node 屬性裡加上 `Firstname` | `Name` |
| `Extract_Node_Event_Network_Domain(T, displayName)` | 在 node 屬性裡加上 `DomainName` | `Url` |
| `Enrich_Node_Ip_Employee(T, displayName)` | 在 IP node 上加員工資訊 | `ClientIp` |
| `Enrich_Node_Username_Employee(T, displayName)` | 在使用者 node 上加員工資訊 | `Username` |
| `Enrich_Node_Event_Authentication_Username(T, displayName)` | 加上認證上下文 | `Username` |
| `Enrich_Node_Ip_Domain(T, displayName)` | 加上 DNS 網域 | `ClientIp` |
| `Enrich_Node_Ip_Event_NetworkOutbound(T, displayName)` | 加上對外事件 | `ClientIp` |
| `Enrich_Graph_Ip_Employee(T, mappingJson)` | 用員工 node 擴充 graph | `ClientIp` |
| `Enrich_Graph_Username_Employee(T, mappingJson)` | 用員工 node 擴充 graph | `Username` |
| `Enrich_Graph_Event_Authentication_Username(T, mappingJson)` | 用認證 node 擴充 | `Username` |

## 對應 JSON Schema

JSON 對應有兩個陣列：`node_types` 和 `edges`。

### `node_types[]`

| 欄位 | 必填 | 說明 |
|---|---|---|
| `type` | 是 | Node 型別標籤（例如 `"User"`、`"Host"`、`"IP"`） |
| `id` | 是 | Node ID 的前綴；通常跟 type 一樣 |
| `key` | 是 | 欄位名稱，它的值會成為 node 的身分 |
| `props` | 是 | 要當作 node 屬性帶過去的欄位陣列 |
| `defaults` | 否 | null/空屬性的備用值物件 |
| `defIcon` | 否 | 這個 node 型別的預設圖示 URL |
| `displayName` | 否 | 用來當顯示標籤的欄位（預設是 `id`） |
| `color` | 否 | 取顏色的來源欄位 |
| `size` | 否 | 取大小的來源欄位 |

### `edges[]`

| 欄位 | 必填 | 說明 |
|---|---|---|
| `type` | 是 | Edge 型別標籤（例如 `"AuthenticatesTo"`、`"SentEmail"`） |
| `source` | 是 | `{"id": "<prefix>", "type": "<NodeType>"}` |
| `target` | 是 | `{"id": "<prefix>", "type": "<NodeType>"}` |
| `props` | 否 | 要當作 edge 屬性帶過去的欄位陣列 |
| `displayName` | 否 | Edge 標籤用的欄位 |
| `color` | 否 | Edge 顏色用的欄位 |

### 圖示庫

圖示用 `https://raw.githubusercontent.com/benc-uk/icon-collection/master/azure-icons/` 裡的：
- IP：`Public-IP-Addresses-(Classic).svg`
- Host/VM：`Virtual-Machine.svg`
- User：`Users.svg`
- Email：`Mailbox.svg`（或 `azure-cds/command-1070-Mail.svg`）
- Process：`App-Services.svg`
- File：`Storage-Accounts.svg`
- Alert：`Activity-Log.svg`
- Domain：`DNS-Zones.svg`

## 對應產生規則

給定使用者提供的查詢欄位和對 graph 的描述，依下面步驟產生對應 JSON：

1. **找出實體** -> 每個不同的名詞變成一個 `node_type`
2. **找出關係** -> 每個動詞/介系詞變成一條 `edge`
3. **對應到欄位** -> 用提供的查詢實際產出的欄位；絕對不要假設有不存在的欄位
4. **設定方向** -> source 是動作的執行者，target 是被作用的對象
5. **加上屬性** -> 納入跟調查有關的欄位（時間戳、結果、hash）
6. **指定圖示** -> 依實體類型從上面的圖示集挑

### 欄位參考（IRQL 統一 schema）

| 實體 | Key 欄位 | 可用屬性 |
|---|---|---|
| User | `Username` | `Username`, `Name`, `Role`, `Email` |
| Host | `Hostname` | `Hostname` |
| IP | `ClientIp` | `ClientIp` |
| Email Message | `Subject` | `EnvTime`, `Subject`, `Verdict`, `Url` |
| Sender | `EmailSender` | `EmailSender`, `Domain` |
| Recipient | `EmailRecipient` | `EmailRecipient` |
| Process | `ProcessName` | `EnvTime`, `ProcessName`, `ProcessCommandLine`, `ProcessHash` |
| File | `Filename` | `EnvTime`, `Filename`, `Path`, `Sha256` |
| Domain | `DomainName` | `DomainName` |
| Auth Event | （合成 ID） | `EnvTime`, `UserAgent`, `Result`, `Description` |

## Function 選擇

1. 從使用者提供的 KQL/IRQL 表格 pipeline 開始。
2. 用 `Lift_To_Graph(mapping)` 建立 graph 實體。
3. 只有在使用者要求、且跟對應的 key 相容時，才加 `Extract_Node_*`、`Enrich_Node_*` 或 `Enrich_Graph_*`。
4. 只有要求分組/收合時，才加 `Graph_Fold_By_Property()`。
5. 視覺化輸出以 `Graph_Render_View()` 結尾。
6. 對 pipeline 選用的每個 stored function 做前置檢查。

## Pipeline 模式

```kql
// 1. 保留使用者提供的 KQL 或 IRQL 查詢
<input query>
// 2. Lift 成 graph
| invoke Lift_To_Graph(<mapping_json>)
// 3. 選用：擷取或補充 graph 實體
| invoke <Extract_Node_* | Enrich_Node_* | Enrich_Graph_*>()
// 4. 選用：有要求才折疊 node
| invoke Graph_Fold_By_Property("<NodeType>", "<PropertyName>")
// 5. 渲染
| invoke Graph_Render_View()
```

## 範例

更多 prompt 和實作範例見 [references/EXAMPLES.md](references/EXAMPLES.md)。

### 認證 graph：IP -> AuthEvent -> User -> Host

**輸入查詢**：`Get_Event_Authentication_All | where Result == "Failed Login" | take 200`

**Graph 需求**：「顯示 IP、認證事件、使用者和主機；依結果折疊事件。」

```kql
let auth_mapping = '{"node_types":[{"type":"SrcIp","id":"SrcIp","key":"ClientIp","props":["ClientIp"],"defaults":{},"defIcon":"https://raw.githubusercontent.com/benc-uk/icon-collection/master/azure-icons/Public-IP-Addresses-(Classic).svg"},{"type":"Host","id":"Host","key":"Hostname","props":["Hostname"],"defaults":{},"defIcon":"https://raw.githubusercontent.com/benc-uk/icon-collection/master/azure-icons/Virtual-Machine.svg"},{"type":"User","id":"User","key":"Username","props":["Username"],"defaults":{},"defIcon":"https://raw.githubusercontent.com/benc-uk/icon-collection/master/azure-icons/Users.svg"},{"type":"AuthEvent","id":"AuthEvent","key":"AuthEventId","props":["AuthEventId","EnvTime","UserAgent","Result","Description"],"defaults":{"Result":"unknown"},"defIcon":"https://raw.githubusercontent.com/benc-uk/icon-collection/master/azure-icons/Activity-Log.svg"}],"edges":[{"type":"RequestsAuth","source":{"id":"SrcIp","type":"SrcIp"},"target":{"id":"AuthEvent","type":"AuthEvent"},"props":["EnvTime"]},{"type":"TargetsUser","source":{"id":"AuthEvent","type":"AuthEvent"},"target":{"id":"User","type":"User"},"props":["EnvTime"]},{"type":"AgainstHost","source":{"id":"AuthEvent","type":"AuthEvent"},"target":{"id":"Host","type":"Host"},"props":["EnvTime"]}]}';
Get_Event_Authentication_All
| extend AuthEventId = strcat(Username, "_", Hostname, "_", EnvTime)
| where Result == "Failed Login"
| take 200
| invoke Lift_To_Graph(auth_mapping)
| invoke Graph_Fold_By_Property("AuthEvent", "Result")
| invoke Graph_Render_View()
```

### Email graph：Sender -> Message -> Recipient

**輸入查詢**：`Get_Email_All | take 400`

**Graph 需求**：「視覺化寄件者到信件到收件者的流向，並依 verdict 折疊信件。」

```kql
let mail_mapping = '{"node_types":[{"type":"EmailMessage","id":"Message","key":"Subject","props":["EnvTime","Subject","Verdict"],"defaults":{},"defIcon":"https://raw.githubusercontent.com/benc-uk/icon-collection/master/azure-icons/Media-File.svg"},{"type":"Sender","id":"Email","key":"EmailSender","props":["EmailSender"],"defaults":{},"defIcon":"https://raw.githubusercontent.com/benc-uk/icon-collection/master/azure-cds/command-1070-Mail.svg"},{"type":"Recipient","id":"Email","key":"EmailRecipient","props":["EmailRecipient"],"defaults":{},"defIcon":"https://raw.githubusercontent.com/benc-uk/icon-collection/master/azure-cds/command-1070-Mail.svg"}],"edges":[{"type":"SentBy","source":{"id":"Message","type":"EmailMessage"},"target":{"id":"Email","type":"Sender"},"props":["EnvTime","Verdict"]},{"type":"DeliveredTo","source":{"id":"Message","type":"EmailMessage"},"target":{"id":"Email","type":"Recipient"},"props":["EnvTime","Verdict"]}]}';
Get_Email_All
| take 400
| invoke Lift_To_Graph(mail_mapping)
| invoke Graph_Fold_By_Property("EmailMessage", "Verdict")
| invoke Graph_Render_View()
```

### 可疑網域調查（端到端）

**基本來源需求**：「用這些可疑網域的對外網路事件，畫出 IP 到網域的連線，並補上員工姓名。」

這是有限度的 fallback：一個已知 selector、一個 extractor、一個直接的過濾條件。

```kql
let suspicious_domain_mapping = '{"node_types":[{"type":"IP","id":"IP","key":"ClientIp","props":["ClientIp"],"defaults":{},"defIcon":"https://raw.githubusercontent.com/benc-uk/icon-collection/master/azure-icons/Public-IP-Addresses-(Classic).svg"},{"type":"Domain","id":"Domain","key":"DomainName","props":["DomainName"],"defaults":{},"defIcon":"https://raw.githubusercontent.com/benc-uk/icon-collection/master/azure-icons/DNS-Zones.svg"}],"edges":[{"type":"ConnectsTo","source":{"id":"IP","type":"IP"},"target":{"id":"Domain","type":"Domain"},"props":["EnvTime"]}]}';
Get_Event_NetworkOutbound
| invoke Extract_Event_Network_Domain()
| where DomainName has_any ("raisinkanes.com", "nothing-to-see-here.net", "totally-legit-domain.com")
| invoke Lift_To_Graph(suspicious_domain_mapping)
| invoke Enrich_Node_Ip_Employee("Name")
| invoke Graph_Fold_By_Property("Domain", "DomainName")
| invoke Graph_Render_View()
```

### Process 執行 graph：User -> Process -> ParentProcess

**輸入查詢**：`Get_Event_Process_All | where ProcessCommandLine has "powershell" | take 300`

**Graph 需求**：「視覺化 process、父 process、主機和使用者之間的關係。」

```kql
let proc_mapping = '{"node_types":[{"type":"Process","id":"Proc","key":"ProcessName","props":["ProcessName","ProcessCommandLine","ProcessHash"],"defaults":{},"defIcon":"https://raw.githubusercontent.com/benc-uk/icon-collection/master/azure-icons/App-Services.svg"},{"type":"ParentProcess","id":"Proc","key":"ParentProcessName","props":["ParentProcessName","ParentProcessHash"],"defaults":{},"defIcon":"https://raw.githubusercontent.com/benc-uk/icon-collection/master/azure-icons/App-Services.svg"},{"type":"Host","id":"Host","key":"Hostname","props":["Hostname"],"defaults":{},"defIcon":"https://raw.githubusercontent.com/benc-uk/icon-collection/master/azure-icons/Virtual-Machine.svg"},{"type":"User","id":"User","key":"Username","props":["Username"],"defaults":{},"defIcon":"https://raw.githubusercontent.com/benc-uk/icon-collection/master/azure-icons/Users.svg"}],"edges":[{"type":"SpawnedBy","source":{"id":"Proc","type":"Process"},"target":{"id":"Proc","type":"ParentProcess"},"props":["EnvTime"]},{"type":"RanOn","source":{"id":"Proc","type":"Process"},"target":{"id":"Host","type":"Host"},"props":["EnvTime"]},{"type":"ExecutedBy","source":{"id":"Proc","type":"Process"},"target":{"id":"User","type":"User"},"props":["EnvTime"]}]}';
Get_Event_Process_All
| where ProcessCommandLine has "powershell"
| take 300
| invoke Lift_To_Graph(proc_mapping)
| invoke Graph_Render_View()
```

## 查詢結果 -> 對應的轉換

使用者提供查詢並描述想要的 graph 時：

1. 檢查查詢最後輸出的欄位
2. 解析實體名詞和關係動詞
3. 只用那些欄位產生對應 JSON
4. 保留使用者提供的 pipeline，在後面加上 `Lift_To_Graph()`
5. 結尾放上 `Graph_Render_View()`
6. 如果使用者提到分組/收合，而且該 function 存在，就加上 `Graph_Fold_By_Property()`

必要 function 的前置檢查通過之後，輸出完整的 KQL：使用者提供的查詢，加上用字串 `let` 綁定內嵌的對應 JSON。如果無法檢查目標資料庫，就清楚標示尚未驗證的 function 相依性。

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
