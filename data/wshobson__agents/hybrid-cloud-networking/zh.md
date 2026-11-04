---
name: hybrid-cloud-networking
description: 用 VPN 和專線設定地端基礎設施與雲端平台之間安全、高效能的連線。適用於建構混合雲架構、把資料中心連到雲端，或實作安全的跨站網路的時候。
---

# 混合雲網路

用 VPN、Direct Connect、ExpressRoute、Interconnect 和 FastConnect，設定地端與雲端環境之間安全、高效能的連線。

## 目的

在地端資料中心與雲端供應商（AWS、Azure、GCP、OCI）之間，建立安全又可靠的網路連線。

## 什麼時候用

- 把地端連到雲端
- 把資料中心延伸到雲端
- 實作混合式的 active-active 架構
- 滿足合規需求
- 逐步遷移到雲端

## 連線選項

### AWS 連線

#### 1. Site-to-Site VPN

- 透過網際網路的 IPSec VPN
- 每條 tunnel 最高 1.25 Gbps
- 中等頻寬時成本效益高
- 延遲較高，依賴網際網路

```hcl
resource "aws_vpn_gateway" "main" {
  vpc_id = aws_vpc.main.id
  tags = {
    Name = "main-vpn-gateway"
  }
}

resource "aws_customer_gateway" "main" {
  bgp_asn    = 65000
  ip_address = "203.0.113.1"
  type       = "ipsec.1"
}

resource "aws_vpn_connection" "main" {
  vpn_gateway_id      = aws_vpn_gateway.main.id
  customer_gateway_id = aws_customer_gateway.main.id
  type                = "ipsec.1"
  static_routes_only  = false
}
```

#### 2. AWS Direct Connect

- 專用的網路連線
- 1 Gbps 到 100 Gbps
- 延遲較低，頻寬穩定
- 比較貴，需要設置時間

**參考：** 請見 `references/direct-connect.md`

### Azure 連線

#### 1. Site-to-Site VPN

```hcl
resource "azurerm_virtual_network_gateway" "vpn" {
  name                = "vpn-gateway"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name

  type     = "Vpn"
  vpn_type = "RouteBased"
  sku      = "VpnGw1"

  ip_configuration {
    name                          = "vnetGatewayConfig"
    public_ip_address_id          = azurerm_public_ip.vpn.id
    private_ip_address_allocation = "Dynamic"
    subnet_id                     = azurerm_subnet.gateway.id
  }
}
```

#### 2. Azure ExpressRoute

- 透過連線供應商的私人連線
- 最高 100 Gbps
- 低延遲、高可靠度
- 全球連線需要 Premium

### GCP 連線

#### 1. Cloud VPN

- IPSec VPN（Classic 或 HA VPN）
- HA VPN：99.99% SLA
- 每條 tunnel 最高 3 Gbps

#### 2. Cloud Interconnect

- Dedicated（10 Gbps、100 Gbps）
- Partner（50 Mbps 到 50 Gbps）
- 延遲比 VPN 低

### OCI 連線

#### 1. IPSec VPN Connect

- 具備備援 tunnel 的 IPSec VPN
- 透過 DRG 做動態路由
- 適合分公司和遷移階段

#### 2. OCI FastConnect

- 透過 Oracle 或合作夥伴邊緣的私人專用連線
- 適合可預期的吞吐量，以及延遲較低的混合流量
- 常搭配 DRG 做 hub-and-spoke 設計

## 混合網路模式

### 模式 1：Hub-and-Spoke

```
地端資料中心
         ↓
    VPN/Direct Connect
         ↓
    Transit Gateway (AWS) / vWAN (Azure)
         ↓
    ├─ Production VPC/VNet
    ├─ Staging VPC/VNet
    └─ Development VPC/VNet
```

### 模式 2：多 Region 混合

```
地端
    ├─ Direct Connect → us-east-1
    └─ Direct Connect → us-west-2
            ↓
        Cross-Region Peering
```

### 模式 3：多雲混合

```
地端資料中心
    ├─ Direct Connect → AWS
    ├─ ExpressRoute → Azure
    ├─ Interconnect → GCP
    └─ FastConnect → OCI
```

## 路由設定

### BGP 設定

```
地端路由器：
- AS Number: 65000
- Advertise: 10.0.0.0/8

雲端路由器：
- AS Number: 64512 (AWS), 65515 (Azure), GCP/OCI 由供應商分配
- Advertise: 雲端 VPC/VNet 的 CIDR
```

### 路由傳播

- 在路由表上啟用路由傳播
- 使用 BGP 做動態路由
- 實作路由過濾
- 監控路由通告

## 安全最佳實務

1. **使用私人連線**（Direct Connect/ExpressRoute/Interconnect/FastConnect）
2. **為 VPN tunnel 實作加密**
3. **使用 VPC endpoint** 避免走網際網路路由
4. **設定 network ACL** 和 security group
5. **啟用 VPC Flow Logs** 以便監控
6. **實作 DDoS 防護**
7. **使用 PrivateLink/Private Endpoint**
8. **用 CloudWatch/Azure Monitor/Cloud Monitoring/OCI Monitoring 監控連線**
9. **實作備援**（雙 tunnel）
10. **定期做安全稽核**

## 高可用性

### 雙 VPN Tunnel

```hcl
resource "aws_vpn_connection" "primary" {
  vpn_gateway_id      = aws_vpn_gateway.main.id
  customer_gateway_id = aws_customer_gateway.primary.id
  type                = "ipsec.1"
}

resource "aws_vpn_connection" "secondary" {
  vpn_gateway_id      = aws_vpn_gateway.main.id
  customer_gateway_id = aws_customer_gateway.secondary.id
  type                = "ipsec.1"
}
```

### Active-Active 設定

- 來自不同地點的多條連線
- 用 BGP 做自動 failover
- Equal-cost multi-path（ECMP）路由
- 監控所有連線的健康狀態

## 監控與疑難排解

### 關鍵指標

- Tunnel 狀態（up/down）
- 進/出的位元組數
- 封包遺失
- 延遲
- BGP session 狀態

### 疑難排解

```bash
# AWS VPN
aws ec2 describe-vpn-connections
aws ec2 get-vpn-connection-telemetry

# Azure VPN
az network vpn-connection show
az network vpn-connection show-device-config-script

# OCI IPSec VPN
oci network ip-sec-connection list
oci network cpe list
```

## 成本最佳化

1. **依流量調整連線大小**
2. **低頻寬的工作負載用 VPN**
3. **把流量集中**到較少的連線
4. **降低資料傳輸**成本
5. **高頻寬用專用的私人連結**
6. **實作快取**以減少流量


## 相關 Skill

- `multi-cloud-architecture`：用於架構決策
- `terraform-module-library`：用於 IaC 實作
