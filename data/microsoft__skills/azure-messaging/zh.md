---
name: azure-messaging
description: "排除 Event Hubs 和 Service Bus 的 Azure Messaging SDK 問題。涵蓋連線失敗、認證錯誤、訊息處理問題和 SDK 設定問題。WHEN: event hub SDK error, service bus SDK issue, messaging connection failure, AMQP error, event processor host issue, message lock lost, message lock expired, lock renewal, lock renewal batch, send timeout, receiver disconnected, SDK troubleshooting, azure messaging SDK, event hub consumer, service bus queue issue, topic subscription error, enable logging event hub, service bus logging, eventhub python, servicebus java, eventhub javascript, servicebus dotnet, event hub checkpoint, event hub not receiving messages, service bus dead letter, batch processing lock, session lock expired, idle timeout, connection inactive, link detach, slow reconnect, session error, duplicate events, offset reset, receive batch."
license: MIT
metadata:
  author: Microsoft
  version: "1.2.1"
---

# Azure Messaging SDK 故障排除

## 快速參考

| 屬性 | 值 |
|----------|-------|
| **服務** | Azure Event Hubs、Azure Service Bus |
| **MCP 工具** | `mcp_azure_mcp_eventhubs`、`mcp_azure_mcp_servicebus` |
| **適用於** | 診斷 SDK 連線、認證和訊息處理問題 |

## 何時使用這個 Skill

- SDK 連線失敗、認證錯誤，或 AMQP link 錯誤
- 閒置逾時、連線不活動，或斷線後重連很慢
- AMQP link detach 或 detach-forced 錯誤
- 訊息鎖遺失、訊息鎖過期、鎖續約失敗，或批次鎖逾時
- Session 鎖遺失、session 鎖過期，或 session receiver 錯誤
- Event processor 或 message handler 停止處理
- 重複事件，或 checkpoint offset 被重設
- SDK 設定問題（retry、prefetch、batch size、receive batch 行為）

## MCP 工具

| 工具 | 指令 | 用途 |
|------|---------|-----|
| `mcp_azure_mcp_eventhubs` | Namespace/hub 操作 | 列出 namespace、hub、consumer group |
| `mcp_azure_mcp_servicebus` | Queue/topic 操作 | 列出 namespace、queue、topic、subscription |
| `mcp_azure_mcp_monitor` | `logs_query` | 用 KQL 查診斷 log |
| `mcp_azure_mcp_resourcehealth` | `get` | 檢查服務健康狀態 |
| `mcp_azure_mcp_documentation` | 文件搜尋 | 到 Microsoft Learn 搜尋故障排除文件 |

## 診斷流程

1. **確認 SDK 和版本**：從 prompt 裡找 SDK 和版本的線索；沒寫的話，先繼續診斷，需要時再問
2. **檢查資源健康狀態**：用 `mcp_azure_mcp_resourcehealth` 確認 namespace 是健康的
3. **檢視錯誤訊息**：對照各語言專屬的故障排除指南
4. **查文件**：用 `mcp_azure_mcp_documentation` 到 Microsoft Learn 搜尋該錯誤或主題
5. **檢查設定**：確認連線字串、entity 名稱、consumer group
6. **建議修正**：套用處理方式，並引用找到的文件


## 故障排除指南

連線、SDK 和認證的故障排除指南放在 azure-diagnostics skill 的 `troubleshooting/messaging/` 底下。

## 參考資料

- 用 `mcp_azure_mcp_documentation` 到 Microsoft Learn 搜尋最新的指引。
