---
name: azure-kusto-graph
description: "用自然語言建立並查詢 Kusto graph。涵蓋暫時性 graph（make-graph）、持久化 graph model/snapshot、模式比對（graph-match）、最短路徑、連通元件，以及 graph 匯出成 table。產生「edges 優先」的思考方式：定義 edges、定義 node lookup、union、make-graph。WHEN: make-graph, graph-match, graph-shortest-paths, graph-to-table, graph-mark-components, persistent graph, graph model, graph snapshot, build a graph from data, find paths between nodes, pattern matching in graph, connected components, transient graph, Kusto graph, KQL graph."
license: MIT
metadata:
  author: Microsoft
  version: "1.2.1"
---

# Kusto Graph 語意

用 KQL 的 graph 運算子，從表格資料建立暫時性和持久化的 graph。這個 skill 把自然語言轉成「edges 優先」的 graph 建構模式，以及 graph 查詢運算子。

## 啟動條件

使用者有以下情況時用這個 skill：
- 想從表格資料建立 graph（`make-graph`）
- 要找資料裡的模式、路徑或關係
- 提到 `graph-match`、`graph-shortest-paths`、`graph-to-table`、`graph-mark-components`
- 想建立持久化的 graph model 或 snapshot
- 說「build a graph」、「find the shortest path」、「find connected components」、「show relationships」
- 問暫時性 graph 和持久化 graph 的差別

**這不是自然語言轉 KQL 的轉換器。** 輸入通常應該是一個能跑的 KQL 查詢（使用者想把它的結果轉成 graph），加上一段用自然語言描述想要的 graph 結構。只有在能直接對應到已知 table、欄位又很明顯時，才支援基本的自然語言來源需求。一般的自然語言轉 KQL，請用專門的查詢產生 skill（另外提供）。

**搭配的 skill：**
- `azure-kusto-irql`：可組合的資安查詢基本元件，產出 graph 要用的表格輸入
- `azure-kusto-irql-graph`：IRQL 的 `Lift_To_Graph` JSON 對應系統，用於在 Kusto Explorer 裡做出型別豐富、帶圖示的 graph

## Edges 優先的做法

在 Kusto 裡建 graph 的基本模式：

```
1. Define your EDGES       -> src --> dest, with relationship type/properties
2. Define your NODE LOOKUPS -> display names, types, properties for each node ID
3. Union edge types         -> if you have multiple relationship types
4. Union node lookups       -> if you have multiple node types
5. Call make-graph          -> edges | make-graph Source --> Target with nodes on nodeId
```

用 `make-graph` 就是這樣思考。Edges 是你在意的關係。Nodes 是 lookup table，替那些 ID 配上臉：顯示名稱、型別、屬性。

## Graph 運算子參考

### `make-graph`：從 table 建立 graph

```kql
Edges | make-graph SourceId --> TargetId with Nodes on NodeId
```

- `Edges`：表格來源，每一列是一條 edge
- `SourceId --> TargetId`：放來源和目標 node ID 的欄位
- `with Nodes on NodeId`：選用的 node 屬性 table，依 ID join
- 支援多個 node table：`with Nodes1 on Id1, Nodes2 on Id2`
- 出現在 edges 裡、但 node table 裡沒有的 node，屬性會是空的

### `graph-match`：找模式

```kql
G | graph-match (a)-[e]->(b) where <constraints> project <output>
```

模式寫法：

| 元素 | 具名 | 匿名 |
|---|---|---|
| Node | `(n)` | `()` |
| Edge 左到右 | `-[e]->` | `-->` |
| Edge 右到左 | `<-[e]-` | `<--` |
| 任一方向 | `-[e]-` | `--` |
| 可變長度 | `-[e*1..5]->` | `-[*1..5]->` |

多跳模式：`(a)-[e1]->(b)-[e2]->(c)`
星狀模式：`(a)--(center)--(b), (c)--(center)--(d)`
環的控制：`cycles = all | none | unique_edges`（預設：`unique_edges`）

### `graph-shortest-paths`：找最短路徑

```kql
G | graph-shortest-paths (start)-[e*1..20]->(end)
      where start.name == "Alice" and end.name == "Server01"
      project Path = e, Length = array_length(e)
```

- 至少要有一條可變長度的 edge
- `output = any`（預設，每一對回傳一條路徑）或 `output = all`（所有同樣長度的最短路徑）
- 可變長度 edge 的屬性會以 dynamic array 回傳

### `graph-to-table`：把 graph 匯出成 table

```kql
G | graph-to-table nodes                                     // 匯出 nodes
G | graph-to-table edges                                     // 匯出 edges
G | graph-to-table nodes as N, edges as E                    // 兩個都匯出
G | graph-to-table nodes with_node_id=Id                     // 包含 node 的 hash ID
G | graph-to-table edges with_source_id=Src with_target_id=Tgt  // 包含 edge 兩端的 ID
```

### `graph-mark-components`：找連通元件

```kql
G | graph-mark-components with_component_id=ComponentId
  | graph-to-table nodes
  | summarize Members = make_list(name) by ComponentId
```

幫每個 node 指派一個 `ComponentId`。同一個連通元件裡的 node 會有相同的 ID。

### `graph()` 函式：查詢持久化 graph

```kql
graph("MyGraphModel")                              // 最新的 snapshot
graph("MyGraphModel", "Snapshot_2025_01")           // 指定的 snapshot
graph("MyGraphModel", true)                         // 依 model 定義建立暫時性 graph
```

## 暫時性 Graph

在查詢執行期間動態建立。不用事先設定。適合臨時分析、探索和做原型。

### 範本：基本的雙實體 graph

```kql
// 1. 定義 edges
let edges = <SourceTable>
    | summarize <aggregations> by SourceCol, TargetCol;
// 2. 定義 node lookup
let source_nodes = edges
    | distinct SourceCol
    | project nodeId = SourceCol, label = SourceCol, nodeType = "<SourceType>";
let target_nodes = edges
    | distinct TargetCol
    | project nodeId = TargetCol, label = TargetCol, nodeType = "<TargetType>";
let all_nodes = union source_nodes, target_nodes;
// 3. 建立 graph 並查詢
edges
| make-graph SourceCol --> TargetCol with all_nodes on nodeId
| graph-match (s)-[e]->(t)
    where <constraints>
    project Source = s.label, Target = t.label, <edge properties>
```

### 範本：多種關係的 graph

```kql
// 多種 edge 類型 -> 用共同的 schema 把它們 union 起來
let auth_edges = AuthEvents
    | project Source = username, Target = hostname, edgeType = "authenticates", ts = timestamp;
let net_edges = NetworkEvents
    | project Source = src_ip, Target = url, edgeType = "connects", ts = timestamp;
let all_edges = union auth_edges, net_edges;
// 從所有來源建立 node lookup
let user_nodes = Employees | project nodeId = username, label = name, nodeType = "User";
let host_nodes = AuthEvents | distinct hostname | project nodeId = hostname, label = hostname, nodeType = "Host";
let all_nodes = union user_nodes, host_nodes;
all_edges
| make-graph Source --> Target with all_nodes on nodeId
```

## 持久化 Graph

用於大規模、可重複使用的 graph。存在資料庫的 metadata 裡。支援 snapshot，可以做歷史比對。

> **安全：** 建立或修改 graph model 和 snapshot 會改動資料庫。執行 `.create-or-alter graph_model` 或 `.make graph_snapshot` 之前，一定要先顯示完整指令並跟使用者確認。

### Step 1：建立 graph model

```kql
.create-or-alter graph_model SecurityGraph
{
  "Schema": {
    "Nodes": {
      "User": {"name": "string", "role": "string"},
      "Host": {"hostname": "string"},
      "IP":   {"ip": "string"}
    },
    "Edges": {
      "AuthenticatesTo": {"timestamp": "datetime", "result": "string"},
      "ConnectsFrom":    {"timestamp": "datetime"}
    }
  },
  "Definition": {
    "Steps": [
      {
        "Kind": "AddNodes",
        "Query": "Employees | project name, role",
        "NodeIdColumn": "name",
        "Labels": ["User"]
      },
      {
        "Kind": "AddNodes",
        "Query": "AuthenticationEvents | distinct hostname | project hostname",
        "NodeIdColumn": "hostname",
        "Labels": ["Host"]
      },
      {
        "Kind": "AddEdges",
        "Query": "AuthenticationEvents | project username, hostname, timestamp, result",
        "SourceColumn": "username",
        "TargetColumn": "hostname",
        "Labels": ["AuthenticatesTo"]
      }
    ]
  }
}
```

### Step 2：建立 snapshot

```kql
.make graph_snapshot SecurityGraph Snapshot_2025_07
```

### Step 3：查詢 snapshot

```kql
graph("SecurityGraph")
| graph-match (user)-[auth]->(host)
    where user.role == "Admin" and auth.result == "Failed Login"
    project User = user.name, Host = host.hostname, Time = auth.timestamp
```

### 管理指令

> **安全：** 底下所有控制指令都會修改或刪除資料庫物件。絕對不准自動執行 `.drop`、`.create-or-alter graph_model` 或 `.make graph_snapshot`。一定要先顯示完整指令、叢集、資料庫和受影響的物件，取得使用者明確確認後才能執行。

```kql
.show graph_models                        // 列出所有 model
.show graph_model SecurityGraph           // 顯示 model 詳細內容
.show graph_snapshots SecurityGraph       // 列出 snapshot
.drop graph_snapshot SecurityGraph Snapshot_2025_07  // 刪除 snapshot（先確認！）
.drop graph_model SecurityGraph           // 刪除 model 和所有 snapshot（先確認！）
```

## 暫時性 vs 持久化：何時用哪個

| 因素 | 暫時性（`make-graph`） | 持久化（`graph()`） |
|---|---|---|
| 設定 | 不用，直接寫在查詢裡 | 要建立 model + snapshot |
| 生命週期 | 只在查詢執行期間 | 存在資料庫 metadata 裡 |
| 資料新鮮度 | 永遠是最新的 | 是建立當下的 snapshot |
| 規模 | 受查詢記憶體限制 | 企業等級 |
| 重複使用 | 每次查詢都重建 | 使用者/查詢之間共用 |
| 最適合 | 臨時的 hunt、做原型 | 正式環境的工作流程、dashboard |

## 資安與威脅獵捕範例

### 認證 graph：誰從哪裡登入了什麼

```kql
let auth_edges = AuthenticationEvents
    | summarize
        logins = count(),
        fails = countif(result == "Failed Login")
      by src_ip, username, hostname;
let ip_nodes = auth_edges | distinct src_ip
    | project nodeId = src_ip, label = src_ip, nodeType = "IP";
let user_nodes = auth_edges | distinct username
    | project nodeId = username, label = username, nodeType = "User";
let host_nodes = auth_edges | distinct hostname
    | project nodeId = hostname, label = hostname, nodeType = "Host";
let all_nodes = union ip_nodes, user_nodes, host_nodes;
// IP -> User 的 edges
let ip_user = auth_edges
    | project Source = src_ip, Target = username, logins, fails;
// User -> Host 的 edges
let user_host = auth_edges
    | project Source = username, Target = hostname, logins, fails;
union ip_user, user_host
| make-graph Source --> Target with all_nodes on nodeId
| graph-match (ip)-[e1]->(user)-[e2]->(host)
    where e2.fails > 20
    project
        IP = ip.label,
        User = user.label,
        Host = host.label,
        Failures = e2.fails
| order by Failures desc
```

### 橫向移動偵測：使用者共用被入侵的主機

```kql
// 模式：(user1)-[auth1]->(host)<-[auth2]-(user2)
// 兩個使用者都在同一台主機上登入失敗 = 可能是 credential spray
let edges = AuthenticationEvents
    | summarize fails = countif(result == "Failed Login"), logins = count()
      by username, hostname;
let nodes = union
    (edges | distinct username | project nodeId = username, nodeType = "User"),
    (edges | distinct hostname | project nodeId = hostname, nodeType = "Host");
edges
| make-graph username --> hostname with nodes on nodeId
| graph-match (u1)-[e1]->(h)<-[e2]-(u2)
    where u1.nodeId != u2.nodeId and e1.fails > 10 and e2.fails > 10
    project
        User1 = u1.nodeId, User2 = u2.nodeId,
        SharedHost = h.nodeId,
        User1Fails = e1.fails, User2Fails = e2.fails
| distinct User1, SharedHost, User2, User1Fails, User2Fails
| order by User1Fails + User2Fails desc
```

### 最短攻擊路徑

```kql
let edges = SecurityEvents
    | project Source = source_entity, Target = target_entity, action, timestamp;
let nodes = union
    (edges | distinct Source | project nodeId = Source),
    (edges | distinct Target | project nodeId = Target);
edges
| make-graph Source --> Target with nodes on nodeId
| graph-shortest-paths (start)-[e*1..10]->(end)
    where start.nodeId == "ExternalIP_1.2.3.4" and end.nodeId == "DatabaseServer"
    project
        PathLength = array_length(e),
        Actions = e.action,
        Hops = e.Target
```

### 連通元件：找出孤立的群集

```kql
let edges = NetworkFlows
    | project Source = src_ip, Target = dst_ip;
let nodes = union
    (edges | distinct Source | project nodeId = Source),
    (edges | distinct Target | project nodeId = Target);
edges
| make-graph Source --> Target with nodes on nodeId
| graph-mark-components with_component_id = ComponentId
| graph-to-table nodes
| summarize Members = make_list(nodeId), Size = count() by ComponentId
| order by Size desc
```

### 在 Kusto Explorer 裡視覺化

查詢在 `make-graph` 就結束（後面不要接 `graph-match`），就會觸發 Kusto Explorer 的互動式 graph 視覺化視窗：

```kql
edges
| make-graph Source --> Target with all_nodes on nodeId
// <- 停在這裡。Kusto Explorer 會把 graph 畫出來。
```

要攤平回 table 給 dashboard 或匯出用，就接 `graph-match | project` 或 `graph-to-table`。

## 搭配 IRQL 使用

處理資安資料時，可以考慮用 `azure-kusto-irql` skill 裡的 IRQL selector（`Get_*`）當資料來源。IRQL 給你統一的 schema，不用背原始的 table 名稱或欄位對應。要有圖示和 node 折疊的豐富視覺化，用 `azure-kusto-irql-graph` skill 的 `Lift_To_Graph` 比較快。

| 做法 | 最適合 |
|---|---|
| 原始 `make-graph`（這個 skill） | 完全掌控、持久化 model、最短路徑、連通元件、自訂 schema |
| `Lift_To_Graph`（`azure-kusto-irql-graph`） | 在 Kusto Explorer 快速做出帶圖示的視覺化、node 折疊 |
| IRQL `Get_*` -> `make-graph` | 用 IRQL 的統一 schema 當輸入，再用原始 graph 運算子分析 |
| IRQL `Get_*` -> `Lift_To_Graph` -> `Graph_Render_View` | 從問題到視覺化 graph 最快的路 |

> **注意：** `Lift_To_Graph`、`Graph_Render_View` 和 `Graph_Fold_By_Property` 是 stored function，不是內建運算子。它們已預先部署在 kc7001 範例叢集上，其他叢集可能需要自己部署。function 定義和部署說明見 `azure-kusto-irql-graph/references/DEPLOY_IRQL_FUNCTIONS.md`。

### 範例：IRQL selector -> make-graph -> 最短路徑

IRQL 負責取資料；`make-graph` 負責 graph 分析。這個範例找出從外部 IP 經過認證事件到郵件伺服器的最短路徑：

```kql
// IRQL 提供統一的欄位（ClientIp, Hostname, Username, Result）
let auth = Get_Event_Authentication_All
    | where Result == "Failed Login";
let edges = auth
    | summarize Failures = count() by ClientIp, Hostname;
let nodes = union
    (edges | distinct ClientIp | project nodeId = ClientIp, nodeType = "IP"),
    (edges | distinct Hostname | project nodeId = Hostname, nodeType = "Host");
edges
| make-graph ClientIp --> Hostname with nodes on nodeId
| graph-shortest-paths (src)-[e*1..5]->(dest)
    where src.nodeType == "IP" and dest.nodeId == "MAIL-SERVER01"
    project
        SourceIP = src.nodeId,
        PathLength = array_length(e),
        Hops = e.Hostname
```

### 範例：IRQL selector -> make-graph -> 連通元件

找出彼此相連的 IP 和網域群集，這些可能是 C2 基礎設施：

```kql
let dns = Get_Dns_All;
let edges = dns | project Source = ClientIp, Target = Domain;
let nodes = union
    (edges | distinct Source | project nodeId = Source, nodeType = "IP"),
    (edges | distinct Target | project nodeId = Target, nodeType = "Domain");
edges
| make-graph Source --> Target with nodes on nodeId
| graph-mark-components with_component_id = ComponentId
| graph-to-table nodes
| summarize
    IPs = make_set_if(nodeId, nodeType == "IP"),
    Domains = make_set_if(nodeId, nodeType == "Domain"),
    Size = count()
  by ComponentId
| where Size > 3
| order by Size desc
```

### 範例：IRQL + make-graph 整合

結合 IRQL selector 和 `make-graph` 的多來源調查 graph，以及 `Lift_To_Graph` 的視覺化 graph 範例，見 [references/EXAMPLES.md](references/EXAMPLES.md)。

## 實際使用情境

完整的實作範例見 [references/SCENARIOS.md](references/SCENARIOS.md)，包括：
- 可達性分析（到關鍵資產的最短路徑）
- 網路分段驗證（連通元件）
- 被入侵帳號的爆炸半徑（可變長度路徑比對）
- 給 SOC 團隊的持久化 graph model（graph_model + snapshot）

## 使用的 MCP 工具

| 工具 | 用途 |
|------|---------|
| `kusto_query` | 執行 KQL 查詢，包括 `make-graph`、`graph-match` 和管理指令 |
| `kusto_table_schema_get` | 建立 edge/node 投影之前，先查 table 有哪些欄位 |
| `kusto_cluster_list` | 列出可用的 ADX 叢集 |
| `kusto_database_list` | 列出叢集裡的資料庫 |

## 在 Kusto Explorer 裡開啟查詢（僅限 Windows）

> **選用的便利功能。** 預設流程是在對話裡輸出 KQL，讓使用者自己複製到 Kusto Explorer 或 VS Code 的 Kusto 擴充套件。自動啟動只在使用者選擇啟用時才做。

### 預設：在對話裡輸出 KQL

一律輸出完整的 KQL，並清楚標示 Step 1（連線）和 Step 2（查詢）：

```
// Step 1: Connect to your cluster (skip if already connected)
// Example: uncomment to connect to the KC7 training cluster
// #connect cluster('kc7001.eastus.kusto.windows.net').database('ValdyTimes')
// Or replace with your own cluster:
// #connect cluster('<YOUR_CLUSTER>').database('<YOUR_DATABASE>')

// Step 2: Run the query below
<KQL_QUERY ending at make-graph>
```

然後緊接著在下面輸出一個 **ADX Web Explorer 版本**，在後面加上 `| graph-to-table nodes as N, edges as E`，因為 ADX Web Explorer 沒辦法直接渲染 `make-graph`：

```
// ADX Web Explorer version (tabular output):
<SAME_QUERY>
| graph-to-table nodes as N, edges as E
```

這樣輸出在 Kusto Explorer（graph 視覺化）和 ADX Web Explorer（表格結果）都能用，使用者不用改任何東西。

### 選用：儲存並啟動

如果使用者要求把查詢存起來或在 Kusto Explorer 裡開啟，照 [references/KUSTO_EXPLORER_LAUNCH.md](references/KUSTO_EXPLORER_LAUNCH.md) 的流程做。重點規則：

- 寫檔或啟動執行檔之前，**一定要**用 `ask_user` 確認
- **一定要**把檔案內容顯示在對話裡，讓使用者開啟前能先檢查
- **絕對不准**用 shell 插值或 here-string，檔案要用 `Set-Content`/`Add-Content` 寫
- **絕對不准**把查詢編碼進瀏覽器 URL
- 在 macOS/Linux 上，存成 `.kql` 檔，然後建議用 VS Code 的 Kusto 擴充套件或 ADX Web Explorer

`make-graph` 的視覺化（graph 視窗）要求查詢**結束在 `make-graph`**，不要接 `graph-match`。Kusto Explorer 只有在輸出是 graph 物件（不是 table）時，才會開 graph 視覺化視窗。
