---
name: multi-cloud-architecture
description: 用決策框架設計 multi-cloud 架構，在 AWS、Azure、GCP 和 OCI 之間選擇並整合服務。在建構 multi-cloud 系統、避免 vendor lock-in，或善用多家供應商各自最強的服務時使用。
---

# Multi-Cloud Architecture

跨 AWS、Azure、GCP 和 OCI 設計應用程式架構的決策框架與模式。

## Purpose

設計不綁定特定雲端的架構，並針對跨雲端供應商的服務選擇做出有根據的決定。

## When to Use

- 設計 multi-cloud 策略
- 在雲端供應商之間遷移
- 為特定 workload 選擇雲端服務
- 實作不綁定特定雲端的架構
- 跨供應商優化成本

## Cloud Service Comparison

### Compute Services

| AWS     | Azure               | GCP             | OCI                 | Use Case           |
| ------- | ------------------- | --------------- | ------------------- | ------------------ |
| EC2     | Virtual Machines    | Compute Engine  | Compute             | IaaS VMs           |
| ECS     | Container Instances | Cloud Run       | Container Instances | Containers         |
| EKS     | AKS                 | GKE             | OKE                 | Kubernetes         |
| Lambda  | Functions           | Cloud Functions | Functions           | Serverless         |
| Fargate | Container Apps      | Cloud Run       | Container Instances | Managed containers |

### Storage Services

| AWS     | Azure           | GCP             | OCI            | Use Case       |
| ------- | --------------- | --------------- | -------------- | -------------- |
| S3      | Blob Storage    | Cloud Storage   | Object Storage | Object storage |
| EBS     | Managed Disks   | Persistent Disk | Block Volumes  | Block storage  |
| EFS     | Azure Files     | Filestore       | File Storage   | File storage   |
| Glacier | Archive Storage | Archive Storage | Archive Storage | Cold storage   |

### Database Services

| AWS         | Azure            | GCP           | OCI                 | Use Case        |
| ----------- | ---------------- | ------------- | ------------------- | --------------- |
| RDS         | SQL Database     | Cloud SQL     | MySQL HeatWave      | Managed SQL     |
| DynamoDB    | Cosmos DB        | Firestore     | NoSQL Database      | NoSQL           |
| Aurora      | PostgreSQL/MySQL | Cloud Spanner | Autonomous Database | Distributed SQL |
| ElastiCache | Cache for Redis  | Memorystore   | OCI Cache           | Caching         |

**參考：** 完整比較請見 `references/service-comparison.md`

## Multi-Cloud Patterns

### Pattern 1: Single Provider with DR

- 主要 workload 放在一個雲端
- Disaster recovery 放在另一個雲端
- 跨雲端的資料庫複寫
- 自動 failover

### Pattern 2: Best-of-Breed

- 每家供應商都挑最好的服務來用
- AI/ML 放 GCP
- 企業應用放 Azure
- 受監管的資料平台放 OCI
- 一般運算放 AWS

### Pattern 3: Geographic Distribution

- 從最近的雲端區域服務使用者
- 符合資料主權要求
- 全球 load balancing
- 區域性 failover

### Pattern 4: Cloud-Agnostic Abstraction

- 運算用 Kubernetes
- 資料庫用 PostgreSQL
- 相容 S3 的儲存（MinIO）
- 開源工具

## Cloud-Agnostic Architecture

### Use Cloud-Native Alternatives

- **運算：** Kubernetes（EKS/AKS/GKE/OKE）
- **資料庫：** PostgreSQL/MySQL（RDS/SQL Database/Cloud SQL/MySQL HeatWave）
- **訊息佇列：** Apache Kafka 或託管的 streaming 服務（MSK/Event Hubs/Confluent/OCI Streaming）
- **快取：** Redis（ElastiCache/Azure Cache/Memorystore/OCI Cache）
- **物件儲存：** 相容 S3 的 API
- **監控：** Prometheus/Grafana
- **Service Mesh：** Istio/Linkerd

### Abstraction Layers

```
Application Layer
    ↓
Infrastructure Abstraction (Terraform)
    ↓
Cloud Provider APIs
    ↓
AWS / Azure / GCP / OCI
```

## Cost Comparison

### Compute Pricing Factors

- **AWS：** On-demand、Reserved、Spot、Savings Plans
- **Azure：** Pay-as-you-go、Reserved、Spot
- **GCP：** On-demand、Committed use、Preemptible
- **OCI：** Pay-as-you-go、年度承諾、burstable/flexible shape、preemptible instance

### Cost Optimization Strategies

1. 使用預留/承諾容量（省 30% 到 70%）
2. 善用 spot/preemptible instance
3. 調整資源到適當大小
4. 對變動的 workload 使用 serverless
5. 優化資料傳輸成本
6. 實作 lifecycle policy
7. 使用成本分攤標籤
8. 用雲端成本工具監控

**參考：** 見 `references/multi-cloud-patterns.md`

## Migration Strategy

### Phase 1: Assessment

- 盤點現有基礎設施
- 找出相依關係
- 評估雲端相容性
- 估算成本

### Phase 2: Pilot

- 挑選試點 workload
- 在目標雲端實作
- 徹底測試
- 記錄學到的經驗

### Phase 3: Migration

- 逐步遷移 workload
- 維持一段雙邊並行期
- 監控效能
- 驗證功能

### Phase 4: Optimization

- 調整資源到適當大小
- 採用雲端原生服務
- 優化成本
- 強化安全性

## Best Practices

1. **使用 infrastructure as code**（Terraform/OpenTofu）
2. **為部署建立 CI/CD pipeline**
3. **跨雲端為失敗做設計**
4. **盡可能使用託管服務**
5. **實作完整的監控**
6. **讓成本優化自動化**
7. **遵循安全最佳實務**
8. **記錄各雲端專屬的設定**
9. **測試 disaster recovery** 程序
10. **訓練團隊**熟悉多個雲端


## Related Skills

- `terraform-module-library` - 用於 IaC 實作
- `cost-optimization` - 用於成本管理
- `hybrid-cloud-networking` - 用於連線
