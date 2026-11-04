---
name: mtls-configuration
description: 設定 mutual TLS（mTLS），達成 zero-trust 的服務對服務通訊。在實作 zero-trust 網路、憑證管理或保護內部服務通訊時使用。
---

# mTLS Configuration

為 zero-trust service mesh 通訊實作 mutual TLS 的完整指南。

## When to Use This Skill

- 實作 zero-trust 網路
- 保護服務對服務的通訊
- 憑證輪替與管理
- 除錯 TLS handshake 問題
- 合規需求（PCI-DSS、HIPAA）
- 多 cluster 的安全通訊

## Core Concepts

### 1. mTLS Flow

```
┌─────────┐                              ┌─────────┐
│ Service │                              │ Service │
│    A    │                              │    B    │
└────┬────┘                              └────┬────┘
     │                                        │
┌────┴────┐      TLS Handshake          ┌────┴────┐
│  Proxy  │◄───────────────────────────►│  Proxy  │
│(Sidecar)│  1. ClientHello             │(Sidecar)│
│         │  2. ServerHello + Cert      │         │
│         │  3. Client Cert             │         │
│         │  4. Verify Both Certs       │         │
│         │  5. Encrypted Channel       │         │
└─────────┘                              └─────────┘
```

### 2. Certificate Hierarchy

```
Root CA (Self-signed, long-lived)
    │
    ├── Intermediate CA (Cluster-level)
    │       │
    │       ├── Workload Cert (Service A)
    │       └── Workload Cert (Service B)
    │
    └── Intermediate CA (Multi-cluster)
            │
            └── Cross-cluster certs
```

## Templates and detailed worked examples

完整的範本庫與詳細的範例放在 `references/details.md`。需要具體範本時，再去讀那個檔案。

## Best Practices

### Do's

- **先從 PERMISSIVE 開始** - 逐步遷移到 STRICT
- **監控憑證到期** - 設定警報
- **使用短效期憑證** - workload 用 24 小時以內
- **定期輪替 CA** - 規劃 CA 的輪替
- **記錄 TLS 錯誤** - 用於除錯與稽核

### Don'ts

- **不要停用 mTLS** - 別為了方便在正式環境這樣做
- **不要忽略憑證到期** - 讓輪替自動化
- **不要用自簽憑證** - 使用正規的 CA 階層
- **不要跳過驗證** - 要驗證完整的憑證鏈
