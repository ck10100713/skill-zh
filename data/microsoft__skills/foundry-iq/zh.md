---
name: foundry-iq
description: "Foundry IQ knowledge base。WHEN: make local or Blob documents searchable; create/diagnose KBs; triage unsupported connectors or multi-source KB creation/reconfiguration (even with classic-search terms); connect existing KB to agents (including multi-source KBs); create/reuse a Search service; retrieve from an existing knowledge base with citations; no brand words needed. Read its procedure before query/target questions. NOT: other KB providers, repository-file search, classic Azure AI Search index/query/app work with no Foundry IQ KB or connector request, generic agent creation."
license: MIT
compatibility: Azure
metadata:
  author: Microsoft
  version: "0.2.2"
---

# Foundry IQ
回答問題或採取動作之前，先讀一份 procedure；叫用 skill 不算讀過。
回覆「被擋下」或「不支援」之前，也要先讀負責的 procedure。
在擬定會變更資源的計畫或取得核准之前，要先成功讀完它必要的 pre-action reference，
只讀被選到的分支。成功讀過的不要重載。失敗時，只能用任何支援的 reader 做有限度、
允許的精確路徑讀取；絕對不要繞過限制或大範圍搜尋。如果還是讀不到：
`blocked: reference-unavailable`，指出缺少的 reference，並說明無法擬定計畫。
絕對不要捏造需求或計畫。
先處理失敗。

清理（cleanup）和有 receipt 支撐的執行，直接交給它們的 lifecycle/producer 負責方；
不要重新打開 Search intake、provisioning 或 hardening。

在做昂貴的服務探索之前，先重用已提供的資源/意圖；否則在一開始問一次
**USE EXISTING / FIND CANDIDATES / CREATE NEW** 的選擇。
只有 FIND 才會列舉；已提供的身分用精確/最小範圍的方式解析。
CREATE 只檢查它提議的名稱，不檢查現有服務的清單。這些回答要跨 source/KB/CU/model 的交接
一路保留；選擇不等於寫入核准。

可搜尋的文件：KB + 經過驗證的 retrieval。意圖只確認一次；只做 KS 必須明確說出來。
子項成功不等於 KB 完成。
不明確/複合/模式/完成：[read](references/intent-routing.md)。

依「要求的操作」來路由，不要依現有 KB 有幾個 source。
連接一個有兩個以上 source 的現有 KB，而且不更動 KB 時，用 Connect。
唯讀操作用它們負責的 procedure 和實際 helper 的限制；
這不會新增 retrieval 模式或支援的 source 種類。
明確不支援的 provisioning，或多 source KB 的建立/重新設定，要用 Diagnose
並在探索之前就停下來，就算同時還要求連接 agent 也一樣。
在複合請求中，這個路由優先於傳統搜尋的術語（例如 hybrid search）。
絕對不要以單純拒絕收場：Diagnose 要給出界線、文件指引和 agent 交接；寫入仍然需要已核准的具體計畫。
不要默默只執行複合請求中支援的那一部分。
如果「連接既有 KB」和「建立/重新設定 KB」分不清楚，要先讀
intent-routing，並在 Azure 探索之前釐清範圍。絕對不要自行推斷要變更 KB。

|Outcome|Read|
|---|---|
|Cleanup|[Plan cleanup](lifecycle/cleanup.md)|
| Failure/drift | [Diagnose](troubleshooting/diagnose.md) |
| Unsupported connector provisioning / multi-source KB creation or reconfiguration | [Diagnose](troubleshooting/diagnose.md) |
| Connect | [Connect](agents/connect.md) |
| Read KB | [Query](knowledge-bases/retrieve.md) |
| Search only | [Search](search-services/create.md) |
| File KS only | [File](knowledge-sources/create-file.md) |
| Blob/ADLS KS only | [Blob](knowledge-sources/create-azure-blob.md) |
| Searchable/KB | [KB](knowledge-bases/create.md) |

一般 agent：`microsoft-foundry`。
讀取：不需要核准；寫入之前要核准沒變動過的計畫。
隱藏 hash。不用 Search/Storage key、不擴大範圍、不猜身分/邊界、
不修復 drift、不把清理和建立放在同一次核准。被接受不等於成功。
