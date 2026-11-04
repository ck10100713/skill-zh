---
name: cost-optimization
description: 透過資源 rightsizing、標籤策略、預留執行個體和支出分析，最佳化 AWS、Azure、GCP 和 OCI 的雲端成本。在降低雲端支出、分析基礎設施成本，或實施成本治理政策時使用。
---

# 雲端成本最佳化

最佳化 AWS、Azure、GCP 和 OCI 雲端成本的策略與模式。

## 目的

實施有系統的成本最佳化策略，在維持效能和可靠性的同時降低雲端支出。

## 何時使用

- 降低雲端支出
- 資源 right-sizing
- 實施成本治理
- 最佳化多雲成本
- 符合預算限制

## 成本最佳化框架

### 1. 可見性

- 實作成本分配標籤
- 使用雲端成本管理工具
- 設定預算警示
- 建立成本 dashboard

### 2. Right-Sizing

- 分析資源使用率
- 縮減過度配置的資源
- 使用 auto-scaling
- 移除閒置資源

### 3. 定價模型

- 使用預留容量
- 善用 spot/preemptible 執行個體
- 實施 savings plan
- 使用承諾使用折扣

### 4. 架構最佳化

- 使用託管服務
- 實作快取
- 最佳化資料傳輸
- 使用 lifecycle policy

## AWS 成本最佳化

### Reserved Instances

```
Savings: 30-72% vs On-Demand
Term: 1 or 3 years
Payment: All/Partial/No upfront
Flexibility: Standard or Convertible
```

### Savings Plans

```
Compute Savings Plans: 66% savings
EC2 Instance Savings Plans: 72% savings
Applies to: EC2, Fargate, Lambda
Flexible across: Instance families, regions, OS
```

### Spot Instances

```
Savings: Up to 90% vs On-Demand
Best for: Batch jobs, CI/CD, stateless workloads
Risk: 2-minute interruption notice
Strategy: Mix with On-Demand for resilience
```

### S3 成本最佳化

```hcl
resource "aws_s3_bucket_lifecycle_configuration" "example" {
  bucket = aws_s3_bucket.example.id

  rule {
    id     = "transition-to-ia"
    status = "Enabled"

    transition {
      days          = 30
      storage_class = "STANDARD_IA"
    }

    transition {
      days          = 90
      storage_class = "GLACIER"
    }

    expiration {
      days = 365
    }
  }
}
```

## Azure 成本最佳化

### Reserved VM Instances

- 1 年或 3 年期
- 最高 72% 的節省
- 彈性的規格
- 可以交換

### Azure Hybrid Benefit

- 使用既有的 Windows Server 授權
- 搭配 RI 最高節省 80%
- 適用於 Windows 和 SQL Server

### Azure Advisor 建議

- Right-size VM
- 刪除未使用的資源
- 使用預留容量
- 最佳化儲存

## GCP 成本最佳化

### Committed Use Discounts

- 1 年或 3 年的承諾
- 最高 57% 的節省
- 適用於 vCPU 和記憶體
- 以資源或以支出為基礎

### Sustained Use Discounts

- 自動折扣
- 執行中的執行個體最高 30%
- 不需要承諾
- 適用於 Compute Engine、GKE

### Preemptible VMs

- 最高 80% 的節省
- 最長執行 24 小時
- 最適合批次工作負載

## OCI 成本最佳化

### Flexible Shapes

- 獨立擴縮 OCPU 和記憶體
- 讓執行個體規格符合工作負載的需求
- 減少固定 VM 規格造成的容量浪費

### 承諾與預算

- 對可預測的支出使用年度承諾
- 設定 compartment 層級、帶警示的預算
- 用 OCI Cost Analysis 追蹤每月的預測

### Preemptible 容量

- 對批次和短暫的工作負載使用 preemptible 執行個體
- 保留能容忍中斷的 autoscaling group
- 對關鍵服務，混用標準容量

## 標籤策略

### AWS 標籤

```hcl
locals {
  common_tags = {
    Environment = "production"
    Project     = "my-project"
    CostCenter  = "engineering"
    Owner       = "team@example.com"
    ManagedBy   = "terraform"
  }
}

resource "aws_instance" "example" {
  ami           = "ami-12345678"
  instance_type = "t3.medium"

  tags = merge(
    local.common_tags,
    {
      Name = "web-server"
    }
  )
}
```

**參考：** 見 `references/tagging-standards.md`

## 成本監控

### 預算警示

```hcl
# AWS Budget
resource "aws_budgets_budget" "monthly" {
  name              = "monthly-budget"
  budget_type       = "COST"
  limit_amount      = "1000"
  limit_unit        = "USD"
  time_period_start = "2024-01-01_00:00"
  time_unit         = "MONTHLY"

  notification {
    comparison_operator        = "GREATER_THAN"
    threshold                  = 80
    threshold_type            = "PERCENTAGE"
    notification_type         = "ACTUAL"
    subscriber_email_addresses = ["team@example.com"]
  }
}
```

### 成本異常偵測

- AWS Cost Anomaly Detection
- Azure Cost Management 警示
- GCP Budget 警示
- OCI Budgets 和 Cost Analysis

## 架構模式

### Pattern 1：Serverless 優先

- 事件驅動的工作用 Lambda/Functions
- 只為執行時間付費
- 內含 auto-scaling
- 沒有閒置成本

### Pattern 2：Right-Sized 的資料庫

```
Development: t3.small RDS
Staging: t3.large RDS
Production: r6g.2xlarge RDS with read replicas
```

### Pattern 3：多層儲存

```
Hot data: S3 Standard
Warm data: S3 Standard-IA (30 days)
Cold data: S3 Glacier (90 days)
Archive: S3 Deep Archive (365 days)
```

### Pattern 4：Auto-Scaling

```hcl
resource "aws_autoscaling_policy" "scale_up" {
  name                   = "scale-up"
  scaling_adjustment     = 2
  adjustment_type        = "ChangeInCapacity"
  cooldown              = 300
  autoscaling_group_name = aws_autoscaling_group.main.name
}

resource "aws_cloudwatch_metric_alarm" "cpu_high" {
  alarm_name          = "cpu-high"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "CPUUtilization"
  namespace           = "AWS/EC2"
  period              = "60"
  statistic           = "Average"
  threshold           = "80"
  alarm_actions       = [aws_autoscaling_policy.scale_up.arn]
}
```

## 成本最佳化檢查清單

- [ ] 實作成本分配標籤
- [ ] 刪除未使用的資源（EBS、EIP、snapshot）
- [ ] 依使用率 right-size 執行個體
- [ ] 對穩定的工作負載使用預留容量
- [ ] 實作 auto-scaling
- [ ] 最佳化儲存類別
- [ ] 使用 lifecycle policy
- [ ] 啟用成本異常偵測
- [ ] 設定預算警示
- [ ] 每週檢視成本
- [ ] 使用 spot/preemptible 執行個體
- [ ] 最佳化資料傳輸成本
- [ ] 實作快取層
- [ ] 使用託管服務
- [ ] 持續監控並最佳化

## 工具

- **AWS：** Cost Explorer、Cost Anomaly Detection、Compute Optimizer
- **Azure：** Cost Management、Advisor
- **GCP：** Cost Management、Recommender
- **OCI：** Cost Analysis、Budgets、Cloud Advisor
- **多雲：** CloudHealth、Cloudability、Kubecost


## 相關 Skill

- `terraform-module-library`：用於資源佈建
- `multi-cloud-architecture`：用於雲端選擇
